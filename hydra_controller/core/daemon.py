import time
import logging
import threading
import winsound
from typing import Optional, Dict, Any, Tuple, Callable
import pygame

from hydra_controller.core.config import DEFAULT_POLL_INTERVAL, DEFAULT_CONNECT_DEBOUNCE, DEFAULT_DISCONNECT_DEBOUNCE, DEFAULT_EXCLUDED_KEYWORDS

logger = logging.getLogger("hydra_bento")


class ControllerDaemon:
    def __init__(
        self,
        get_config: Callable[[], Dict[str, Any]],
        on_controller_change: Callable[[int, str], None],
        on_telemetry_update: Optional[Callable[[Dict[str, float]], None]] = None,
        on_launch_requested: Optional[Callable[[], None]] = None,
        on_kill_requested: Optional[Callable[[], None]] = None,
        on_toast_requested: Optional[Callable[[str, str], None]] = None,
    ):
        self.get_config = get_config
        self.on_controller_change = on_controller_change
        self.on_telemetry_update = on_telemetry_update
        self.on_launch_requested = on_launch_requested
        self.on_kill_requested = on_kill_requested
        self.on_toast_requested = on_toast_requested

        self.is_running = False
        self.monitor_thread: Optional[threading.Thread] = None

        self.current_controller_count = 0
        self.connected_controller_name = ""
        self.battery_status_str = "Standby"
        self.stick_telemetry = {"ls_x": 0.0, "ls_y": 0.0, "rs_x": 0.0, "rs_y": 0.0, "lt": 0.0, "rt": 0.0}
        self.guide_held_since = 0.0

    def start(self):
        if self.monitor_thread and self.monitor_thread.is_alive():
            return
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._run_loop, daemon=True)
        self.monitor_thread.start()

    def stop(self):
        self.is_running = False

    def play_sound_chime(self, is_connect: bool = True):
        cfg = self.get_config()
        if not cfg.get("sound_alerts", True):
            return
        def _beep():
            try:
                freq = 880 if is_connect else 440
                winsound.Beep(freq, 100)
            except Exception:
                pass
        threading.Thread(target=_beep, daemon=True).start()

    def trigger_rumble_test(self):
        try:
            if pygame.joystick.get_count() > 0:
                joy = pygame.joystick.Joystick(0)
                joy.init()
                if hasattr(joy, 'rumble'):
                    joy.rumble(0.7, 0.9, 500)
                    logger.info("Sent 500ms haptic rumble pulse to controller.")
                    self.play_sound_chime(is_connect=True)
                else:
                    logger.info("Rumble interface not supported by active driver.")
        except Exception as e:
            logger.warning(f"Rumble test exception: {e}")

    def check_controllers_fast(self) -> Tuple[int, str]:
        try:
            total_count = pygame.joystick.get_count()
            if total_count == 0:
                return 0, ""

            cfg = self.get_config()
            exclusions = cfg.get("excluded_keywords", DEFAULT_EXCLUDED_KEYWORDS)
            for i in range(total_count):
                try:
                    joy = pygame.joystick.Joystick(i)
                    joy.init()
                    name = joy.get_name()
                    lower_name = name.lower()
                    if not any(keyword in lower_name for keyword in exclusions):
                        return total_count, name
                except Exception:
                    pass
            return 0, ""
        except Exception:
            return 0, ""

    def _run_loop(self):
        try:
            pygame.init()
            pygame.joystick.init()
        except Exception:
            self.is_running = False
            return

        initial_count, initial_name = self.check_controllers_fast()
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
                time.sleep(cfg.get("poll_interval", DEFAULT_POLL_INTERVAL))

                # Lightweight joystick event pump
                pygame.event.pump()
                raw_count, raw_name = self.check_controllers_fast()
                now = time.time()

                # Read hardware telemetry
                if raw_count > 0:
                    try:
                        joy = pygame.joystick.Joystick(0)
                        joy.init()
                        
                        # Power/Battery status
                        if hasattr(joy, 'get_power_level'):
                            lvl = joy.get_power_level()
                            if lvl in ("full", "max"):
                                self.battery_status_str = "🔋 Full (100%)"
                            elif lvl == "medium":
                                self.battery_status_str = "🔋 Medium (~60%)"
                            elif lvl in ("low", "empty"):
                                self.battery_status_str = "🪫 Low (~20%)"
                            elif lvl == "wired":
                                self.battery_status_str = "🔌 USB Wired"
                            elif lvl == "charging":
                                self.battery_status_str = "⚡ Charging"
                            else:
                                self.battery_status_str = "🔋 Connected"

                        # Analog sticks
                        if joy.get_numaxes() >= 2:
                            self.stick_telemetry["ls_x"] = round(joy.get_axis(0), 2)
                            self.stick_telemetry["ls_y"] = round(joy.get_axis(1), 2)
                        if joy.get_numaxes() >= 4:
                            self.stick_telemetry["rs_x"] = round(joy.get_axis(2) if joy.get_numaxes() == 4 else joy.get_axis(3), 2)
                            self.stick_telemetry["rs_y"] = round(joy.get_axis(3) if joy.get_numaxes() == 4 else joy.get_axis(4), 2)
                        if joy.get_numaxes() >= 6:
                            self.stick_telemetry["lt"] = max(0.0, round((joy.get_axis(4) + 1.0) / 2.0, 2))
                            self.stick_telemetry["rt"] = max(0.0, round((joy.get_axis(5) + 1.0) / 2.0, 2))

                        # Guide / L3+R3 Shortcut
                        if cfg.get("guide_shortcut_enabled", True):
                            guide_pressed = False
                            num_btns = joy.get_numbuttons()
                            if num_btns >= 10 and joy.get_button(num_btns - 2) and joy.get_button(num_btns - 1):
                                guide_pressed = True

                            if guide_pressed:
                                if self.guide_held_since == 0.0:
                                    self.guide_held_since = now
                                elif (now - self.guide_held_since) >= 1.2:
                                    logger.info("Guide / L3+R3 shortcut triggered launcher launch!")
                                    if self.on_launch_requested:
                                        self.on_launch_requested()
                                    self.guide_held_since = now + 3.0
                            else:
                                self.guide_held_since = 0.0

                    except Exception:
                        pass

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
                            elif pending_count == 0 and confirmed_count == 0:
                                self.play_sound_chime(is_connect=False)
                                if self.on_toast_requested:
                                    self.on_toast_requested("Controller Disconnected", "Gamepad disconnected.")
                                if cfg.get("kill_on_disconnect", False) and self.on_kill_requested:
                                    self.on_kill_requested()

        except Exception as e:
            logger.error(f"Error in controller daemon loop: {e}")
        finally:
            try:
                pygame.joystick.quit()
                pygame.quit()
            except Exception:
                pass
