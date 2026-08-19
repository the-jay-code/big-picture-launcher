import time
import threading
import logging
import winsound
from typing import Callable, Optional, Dict, Any, Tuple, List
import pygame

from hydra_controller.core.config import (
    DEFAULT_POLL_INTERVAL,
    DEFAULT_CONNECT_DEBOUNCE,
    DEFAULT_DISCONNECT_DEBOUNCE
)

logger = logging.getLogger("hydra_bento")


# =============================================================================
# MODULAR CONTROLLER INPUT TRACKING FUNCTIONS
# =============================================================================
def read_controller_battery(joy: pygame.joystick.Joystick) -> str:
    """Reads power/battery state from the connected gamepad."""
    if hasattr(joy, 'get_power_level'):
        try:
            lvl = joy.get_power_level()
            if lvl in ("full", "max"):
                return "🔋 Full (100%)"
            elif lvl == "medium":
                return "🔋 Medium (~60%)"
            elif lvl in ("low", "empty"):
                return "🪫 Low (~20%)"
            elif lvl == "wired":
                return "🔌 USB Wired"
            elif lvl == "charging":
                return "⚡ Charging"
        except Exception:
            pass
    return "🔋 Connected"


def apply_radial_deadzone(x: float, y: float, deadzone: float = 0.06) -> Tuple[float, float]:
    """Applies a smooth radial deadzone to eliminate sensor resting drift."""
    mag = (x**2 + y**2)**0.5
    if mag < deadzone:
        return 0.0, 0.0
    scale = (mag - deadzone) / max(0.001, (1.0 - deadzone))
    return round(max(-1.0, min(1.0, (x / mag) * scale)), 2), round(max(-1.0, min(1.0, (y / mag) * scale)), 2)


def poll_controller_telemetry(joy: pygame.joystick.Joystick, deadzone: float = 0.06) -> Dict[str, float]:
    """
    Reads analog thumbstick axes and trigger levels with accurate axis mapping and deadzone compensation.
    Returns: Dict containing 'ls_x', 'ls_y', 'rs_x', 'rs_y', 'lt', 'rt'.
    """
    telemetry = {
        "ls_x": 0.0,
        "ls_y": 0.0,
        "rs_x": 0.0,
        "rs_y": 0.0,
        "lt": 0.0,
        "rt": 0.0
    }
    try:
        num_axes = joy.get_numaxes()
        
        # Left Stick: Axis 0 (X) and Axis 1 (Y)
        if num_axes >= 2:
            raw_ls_x = joy.get_axis(0)
            raw_ls_y = joy.get_axis(1)
            telemetry["ls_x"], telemetry["ls_y"] = apply_radial_deadzone(raw_ls_x, raw_ls_y, deadzone)

        # Right Stick: Axis 2 (X) and Axis 3 (Y) in standard SDL2 / XInput
        if num_axes >= 4:
            raw_rs_x = joy.get_axis(2)
            raw_rs_y = joy.get_axis(3)
            telemetry["rs_x"], telemetry["rs_y"] = apply_radial_deadzone(raw_rs_x, raw_rs_y, deadzone)

        # Analog Triggers: Axis 4 (LT) and Axis 5 (RT)
        if num_axes >= 6:
            lt_raw = joy.get_axis(4)
            rt_raw = joy.get_axis(5)
            # Normalize from [-1.0, 1.0] to [0.0, 1.0] with trigger threshold
            lt_val = (lt_raw + 1.0) / 2.0
            rt_val = (rt_raw + 1.0) / 2.0
            telemetry["lt"] = max(0.0, min(1.0, round(lt_val if lt_val > 0.04 else 0.0, 2)))
            telemetry["rt"] = max(0.0, min(1.0, round(rt_val if rt_val > 0.04 else 0.0, 2)))
    except Exception:
        pass
    return telemetry


def poll_controller_buttons(joy: pygame.joystick.Joystick) -> Dict[str, Any]:
    """
    Tracks all physical button presses, D-pad hats, and guide states.
    Returns: Dict containing active button indices and D-pad hat values.
    """
    btn_state = {
        "pressed_buttons": [],
        "dpad": (0, 0),
        "guide_pressed": False,
    }
    try:
        num_buttons = joy.get_numbuttons()
        for i in range(num_buttons):
            if joy.get_button(i):
                btn_state["pressed_buttons"].append(i)

        if joy.get_numhats() > 0:
            btn_state["dpad"] = joy.get_hat(0)

        # Guide / L3+R3 detection
        if num_buttons >= 10:
            if joy.get_button(num_buttons - 2) and joy.get_button(num_buttons - 1):
                btn_state["guide_pressed"] = True
            elif num_buttons > 10 and joy.get_button(10): # Standard Guide button index
                btn_state["guide_pressed"] = True
    except Exception:
        pass
    return btn_state


def process_guide_shortcut(
    guide_pressed: bool,
    now: float,
    held_since: float,
    on_trigger_callback: Optional[Callable[[], None]],
    enabled: bool = True
) -> float:
    """Handles the 1.2-second Guide / L3+R3 hold gesture."""
    if not enabled:
        return 0.0

    if guide_pressed:
        if held_since == 0.0:
            return now
        elif (now - held_since) >= 1.2:
            logger.info("Guide / L3+R3 shortcut triggered launcher launch!")
            if on_trigger_callback:
                on_trigger_callback()
            return now + 3.0  # Cooldown
    else:
        return 0.0

    return held_since


# =============================================================================
# CONTROLLER DAEMON
# =============================================================================
class ControllerDaemon:
    def __init__(
        self,
        get_config: Callable[[], Dict[str, Any]],
        on_controller_change: Callable[[int, str], None],
        on_telemetry_update: Optional[Callable[[Dict[str, float]], None]] = None,
        on_button_update: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_launch_requested: Optional[Callable[[], None]] = None,
        on_kill_requested: Optional[Callable[[], None]] = None,
        on_toast_requested: Optional[Callable[[str, str], None]] = None,
    ):
        self.get_config = get_config
        self.on_controller_change = on_controller_change
        self.on_telemetry_update = on_telemetry_update
        self.on_button_update = on_button_update
        self.on_launch_requested = on_launch_requested
        self.on_kill_requested = on_kill_requested
        self.on_toast_requested = on_toast_requested

        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        self.current_controller_count = 0
        self.connected_controller_name = ""
        self.connected_controllers: List[Dict[str, Any]] = []
        self.battery_status_str = "Standby"
        
        self.stick_telemetry = {
            "ls_x": 0.0,
            "ls_y": 0.0,
            "rs_x": 0.0,
            "rs_y": 0.0,
            "lt": 0.0,
            "rt": 0.0
        }
        self.button_state = {
            "pressed_buttons": [],
            "dpad": (0, 0),
            "guide_pressed": False
        }
        self.guide_held_since = 0.0
        self.active_joysticks: Dict[int, pygame.joystick.Joystick] = {}

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.thread.start()
            logger.info("ControllerDaemon monitor thread started.")

    def stop(self):
        self.is_running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        try:
            self.active_joysticks.clear()
            pygame.joystick.quit()
        except Exception:
            pass
        logger.info("ControllerDaemon stopped.")

    def play_sound_chime(self, is_connect: bool = True):
        cfg = self.get_config()
        if not cfg.get("sound_alerts", True):
            return
        def _play():
            try:
                if is_connect:
                    winsound.Beep(523, 70)
                    winsound.Beep(659, 70)
                    winsound.Beep(784, 110)
                else:
                    winsound.Beep(659, 70)
                    winsound.Beep(523, 110)
            except Exception:
                pass
        threading.Thread(target=_play, daemon=True).start()

    def trigger_rumble_test(self):
        """Sends a 500ms haptic vibration pulse to verify controller rumble motors."""
        try:
            if self.active_joysticks:
                joy = next(iter(self.active_joysticks.values()))
                if hasattr(joy, 'rumble'):
                    joy.rumble(0.6, 0.9, 500)
                    logger.info("Sent rumble test pulse (500ms)")
        except Exception as e:
            logger.warning(f"Rumble test failed: {e}")

    def refresh_connected_controllers(self) -> Tuple[int, str]:
        """Scans connected joysticks without destroying existing initialized instances."""
        try:
            raw_count = pygame.joystick.get_count()
            cfg = self.get_config()
            excluded = [k.lower() for k in cfg.get("excluded_keywords", [])]

            valid_controllers = []
            new_active_map = {}

            for i in range(raw_count):
                try:
                    if i in self.active_joysticks:
                        joy = self.active_joysticks[i]
                    else:
                        joy = pygame.joystick.Joystick(i)
                        joy.init()

                    name = joy.get_name()
                    if any(ex in name.lower() for ex in excluded):
                        continue

                    new_active_map[i] = joy
                    batt = read_controller_battery(joy)
                    valid_controllers.append({
                        "index": i,
                        "name": name,
                        "battery": batt,
                        "num_axes": joy.get_numaxes(),
                        "num_buttons": joy.get_numbuttons(),
                        "num_hats": joy.get_numhats()
                    })
                except Exception:
                    pass

            self.active_joysticks = new_active_map
            self.connected_controllers = valid_controllers
            
            valid_count = len(valid_controllers)
            first_name = valid_controllers[0]["name"] if valid_count > 0 else ""
            return valid_count, first_name

        except Exception as e:
            logger.error(f"Error scanning controllers: {e}")
            return 0, ""

    def _monitor_loop(self):
        try:
            pygame.init()
            pygame.joystick.init()
        except Exception:
            self.is_running = False
            return

        initial_count, initial_name = self.refresh_connected_controllers()
        self.current_controller_count = initial_count
        self.connected_controller_name = initial_name

        confirmed_count = initial_count
        pending_count = initial_count
        pending_name = initial_name
        pending_since = time.time()

        cfg = self.get_config()
        if confirmed_count > 0 and cfg.get("auto_launch_on_controller", True):
            if self.on_launch_requested:
                self.on_launch_requested()

        try:
            while self.is_running:
                cfg = self.get_config()
                poll_delay = 0.02 if confirmed_count > 0 else cfg.get("poll_interval", DEFAULT_POLL_INTERVAL)
                time.sleep(poll_delay)

                # Process event pump (preserves open device handles!)
                pygame.event.pump()
                
                # Check hotplug events if any
                for ev in pygame.event.get():
                    if ev.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                        self.refresh_connected_controllers()

                raw_count = len(self.connected_controllers)
                raw_name = self.connected_controllers[0]["name"] if raw_count > 0 else ""
                now = time.time()

                # Read hardware telemetry directly from the active persistent joystick handle
                if raw_count > 0 and self.active_joysticks:
                    try:
                        primary_joy = next(iter(self.active_joysticks.values()))
                        
                        # 1. Battery State
                        self.battery_status_str = read_controller_battery(primary_joy)

                        # 2. Stick & Trigger Telemetry
                        self.stick_telemetry = poll_controller_telemetry(primary_joy)
                        if self.on_telemetry_update:
                            self.on_telemetry_update(self.stick_telemetry)

                        # 3. Button & D-Pad Tracking
                        self.button_state = poll_controller_buttons(primary_joy)
                        if self.on_button_update:
                            self.on_button_update(self.button_state)

                        # 4. Guide Shortcut
                        self.guide_held_since = process_guide_shortcut(
                            guide_pressed=self.button_state["guide_pressed"],
                            now=now,
                            held_since=self.guide_held_since,
                            on_trigger_callback=self.on_launch_requested,
                            enabled=cfg.get("guide_shortcut_enabled", True)
                        )

                    except Exception:
                        pass

                # Hotplug debounce logic
                if raw_count != pending_count:
                    pending_count = raw_count
                    pending_name = raw_name
                    pending_since = now
                else:
                    if pending_count != confirmed_count:
                        is_connect = pending_count > confirmed_count
                        conn_deb = cfg.get("connect_debounce", DEFAULT_CONNECT_DEBOUNCE)
                        disc_deb = cfg.get("disconnect_debounce", DEFAULT_DISCONNECT_DEBOUNCE)
                        required_debounce = conn_deb if is_connect else disc_deb

                        if (now - pending_since) >= required_debounce:
                            confirmed_count = pending_count
                            self.current_controller_count = confirmed_count
                            self.connected_controller_name = pending_name

                            self.on_controller_change(confirmed_count, pending_name)

                            if is_connect and pending_count > 0:
                                self.play_sound_chime(is_connect=True)
                                if self.on_toast_requested:
                                    self.on_toast_requested("Controller Connected", f"🎮 {pending_name} connected!")
                                if cfg.get("auto_launch_on_controller", True) and self.on_launch_requested:
                                    self.on_launch_requested()
                            elif not is_connect and confirmed_count == 0:
                                self.play_sound_chime(is_connect=False)
                                if self.on_toast_requested:
                                    self.on_toast_requested("Controller Disconnected", "Controller disconnected.")
                                if cfg.get("kill_on_disconnect", False) and self.on_kill_requested:
                                    self.on_kill_requested()

        except Exception as e:
            logger.error(f"Daemon monitor thread encountered error: {e}")
        finally:
            try:
                pygame.joystick.quit()
            except Exception:
                pass
            logger.info("Daemon monitor thread exited.")
