import os
import sys
import time
import threading
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Optional, Dict, Any

import customtkinter as ctk

from hydra_controller.core.config import THEMES, DEFAULT_CONFIG, load_config, save_config
from hydra_controller.core.system import (
    is_windows_startup_enabled,
    set_windows_startup_enabled,
    get_launcher_path,
    find_hydra_exe,
    find_steam_exe,
    find_playnite_exe,
    launch_target_launcher,
    kill_target_launcher,
)
from hydra_controller.core.tray import SystemTrayManager
from hydra_controller.core.daemon import ControllerDaemon
from hydra_controller.ui.geometry import draw_rounded_rect
import importlib
import hydra_controller.ui.pages.dashboard as page_dashboard
import hydra_controller.ui.pages.telemetry as page_telemetry
import hydra_controller.ui.pages.settings as page_settings
import hydra_controller.ui.pages.about as page_about


class BentoHydraApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Live Hot-Reload Timestamp Registry
        self.last_file_mtimes = self._scan_source_mtimes()

        # Configuration & Themes
        self.cfg = load_config()
        self.theme_mode = self.cfg.get("theme_mode", "dark")
        self.theme = THEMES[self.theme_mode]

        # Main Window Specs
        self.title("BP Launcher")
        self.geometry("1120x740")
        self.minsize(1020, 680)
        self.configure(fg_color=self.theme["window_bg"])
        ctk.set_appearance_mode("Dark" if self.theme_mode == "dark" else "Light")

        # Set Window & Taskbar Icon
        icon_ico = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets", "app_icon.ico")
        icon_png = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets", "app_icon.png")
        if os.path.exists(icon_ico):
            try:
                self.iconbitmap(icon_ico)
            except Exception:
                pass
        if os.path.exists(icon_png):
            try:
                img = tk.PhotoImage(file=icon_png)
                self.wm_iconphoto(True, img)
            except Exception:
                pass

        # Runtime State
        self.current_page = "dashboard"
        self.start_time = time.time()
        self.hitboxes: Dict[str, Dict[str, Any]] = {}
        self.hovered_hitbox: Optional[str] = None

        # System Tray Manager
        self.tray_manager = SystemTrayManager(
            on_open=self.show_from_tray,
            on_launch=lambda: threading.Thread(target=self.launch_target_app, daemon=True).start(),
            on_toggle_mon=self.toggle_monitor,
            on_exit=self.exit_app,
        )

        # Controller Daemon
        self.daemon = ControllerDaemon(
            get_config=lambda: self.cfg,
            on_controller_change=self.on_controller_state_change,
            on_telemetry_update=self.on_telemetry_update,
            on_button_update=self.on_button_update,
            on_launch_requested=lambda: threading.Thread(target=self.launch_target_app, daemon=True).start(),
            on_kill_requested=self.kill_target_app,
            on_toast_requested=self.tray_manager.show_toast,
        )

        # Build Canvas & Start
        self.create_layout()
        self.daemon.start()
        self.tray_manager.start(daemon_active=self.daemon.is_running)

        # Animation State
        self.anim_phase = 0.0

        # Force window to foreground on startup
        self.after(200, self._bring_to_front)

        # Live 24/7 UI Heartbeat Pulse Loop
        self.after(50, self._live_heartbeat_tick)

        # In-App Live Hot-Reload Watcher Loop
        self.after(600, self._auto_reload_tick)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    # -------------------------------------------------------------------------
    # Layout & Redraw Engine
    # -------------------------------------------------------------------------
    def create_layout(self):
        self.main_canvas = tk.Canvas(
            self,
            bg=self.theme["window_bg"],
            highlightthickness=0,
            bd=0
        )
        self.main_canvas.pack(fill="both", expand=True, padx=16, pady=16)

        self.main_canvas.bind("<Configure>", lambda e: self.redraw())
        self.main_canvas.bind("<Button-1>", self.on_canvas_click)
        self.main_canvas.bind("<Motion>", self.on_canvas_hover)

        # F5 / Ctrl+R Live Hotkeys
        self.bind("<F5>", lambda e: self.redraw())
        self.bind("<Control-r>", lambda e: self.redraw())

    def set_theme(self, mode: str):
        if mode not in ("dark", "light"):
            return
        self.theme_mode = mode
        self.cfg["theme_mode"] = mode
        self.theme = THEMES[self.theme_mode]
        self.configure(fg_color=self.theme["window_bg"])
        self.main_canvas.configure(bg=self.theme["window_bg"])
        ctk.set_appearance_mode("Dark" if mode == "dark" else "Light")
        save_config(self.cfg)
        self.redraw()

    def toggle_theme(self):
        new_mode = "light" if self.theme_mode == "dark" else "dark"
        self.set_theme(new_mode)

    def redraw(self):
        canvas = self.main_canvas
        w = canvas.winfo_width()
        h = canvas.winfo_height()

        if w < 100 or h < 100:
            return

        canvas.delete("all")
        self.hitboxes.clear()

        pad = 6
        rail_width = 84
        T = self.theme

        # Outer Window Canvas Frame
        draw_rounded_rect(canvas, pad, pad, w - pad, h - pad, radius=24, fill=T["canvas_bg"], outline=T["outer_border"], width=1.5)

        # Left Rail Bounds
        rail_x1 = pad + 12
        rail_y1 = pad + 12
        rail_x2 = rail_x1 + rail_width
        rail_y2 = h - pad - 12

        # Top Logo Badge (BP Monogram)
        sp_size = 54
        sp_x = rail_x1 + (rail_width - sp_size) // 2
        sp_y = rail_y1 + 6
        draw_rounded_rect(canvas, sp_x, sp_y, sp_x + sp_size, sp_y + sp_size, radius=27, fill=T["rail_bg"], outline=T["active_blue"], width=1.8)
        canvas.create_text(sp_x + sp_size//2, sp_y + sp_size//2, text="BP", fill=T["active_blue"], font=("Segoe UI Variable Display", 18, "bold"))
        self.register_hitbox("nav_logo", sp_x, sp_y, sp_x + sp_size, sp_y + sp_size, "Dashboard")

        # Vertical Navigation Capsule
        cap_w = 54
        cap_h = 240
        cap_x1 = rail_x1 + (rail_width - cap_w) // 2
        cap_y1 = sp_y + sp_size + 16
        cap_x2 = cap_x1 + cap_w
        cap_y2 = cap_y1 + cap_h
        draw_rounded_rect(canvas, cap_x1, cap_y1, cap_x2, cap_y2, radius=27, fill=T["rail_bg"], outline=T["outer_border"], width=1.5)

        pages = [
            ("dashboard", "⬚", "Controllers"),
            ("telemetry", "🎮", "Telemetry Lab"),
            ("settings", "⚙", "Settings"),
            ("about", "ℹ", "About"),
        ]

        spacing = (cap_h - 48) / (len(pages) - 1)
        for i, (page_key, icon, label) in enumerate(pages):
            iy = cap_y1 + 24 + i * spacing
            is_active = (self.current_page == page_key)
            bg_col = T["pill_light"] if is_active else T["pill_dark"]
            fg_col = T["text_dark"] if is_active else T["text_muted"]
            r = 15 if is_active else 11

            draw_rounded_rect(canvas, cap_x1 + cap_w//2 - r - 4, iy - r - 4, cap_x1 + cap_w//2 + r + 4, iy + r + 4, radius=r+4, fill=bg_col, outline="")
            canvas.create_text(cap_x1 + cap_w//2, iy, text=icon, fill=fg_col, font=("Segoe UI Symbol", 15, "bold"))
            self.register_hitbox(f"nav_{page_key}", cap_x1, iy - 20, cap_x2, iy + 20, label)

        # Theme Switcher Button (☀️ / 🌙)
        th_size = 46
        th_x = rail_x1 + (rail_width - th_size) // 2
        th_y = cap_y2 + 16
        draw_rounded_rect(canvas, th_x, th_y, th_x + th_size, th_y + th_size, radius=23, fill=T["rail_bg"], outline=T["outer_border"], width=1.5)
        theme_str = "☀" if self.theme_mode == "light" else "☽"
        canvas.create_text(th_x + th_size//2, th_y + th_size//2, text=theme_str, fill=T["active_blue"] if self.theme_mode == "light" else T["text_light"], font=("Segoe UI Symbol", 20, "bold"))
        self.register_hitbox("toggle_theme_btn", th_x, th_y, th_x + th_size, th_y + th_size, "Toggle Theme")

        # Bottom Daemon Status Indicator (Live 24/7 Animated Pulse)
        bot_btn_r = 20
        bot_btn_y = rail_y2 - 28
        bot_bg = T["active_blue"] if self.daemon.is_running else T["danger_red"]
        canvas.create_oval(rail_x1 + rail_width//2 - bot_btn_r - 4, bot_btn_y - bot_btn_r - 4, rail_x1 + rail_width//2 + bot_btn_r + 4, bot_btn_y + bot_btn_r + 4, outline=T["active_blue_bg"] if self.daemon.is_running else "", width=2, tags=("daemon_pulse_ring",))
        canvas.create_oval(rail_x1 + rail_width//2 - bot_btn_r, bot_btn_y - bot_btn_r, rail_x1 + rail_width//2 + bot_btn_r, bot_btn_y + bot_btn_r, fill=T["rail_bg"], outline=bot_bg, width=2.5)
        canvas.create_text(rail_x1 + rail_width//2, bot_btn_y, text="●", fill=bot_bg, font=("Segoe UI", 14, "bold"), tags=("daemon_dot",))
        self.register_hitbox("toggle_monitor_state", rail_x1 + 6, bot_btn_y - bot_btn_r, rail_x1 + rail_width - 6, bot_btn_y + bot_btn_r, "Toggle Daemon Monitoring")

        # Main Viewport Routing
        cx1 = rail_x2 + 16
        cy1 = pad + 12
        cx2 = w - pad - 12
        cy2 = h - pad - 12

        if self.current_page == "dashboard":
            page_dashboard.draw_dashboard_page(
                canvas=canvas,
                theme=self.theme,
                profile=self.get_active_profile(),
                is_running=self.daemon.is_running,
                target_name=self.get_target_launcher_name(),
                controller_count=self.daemon.current_controller_count,
                connected_controllers=self.daemon.connected_controllers,
                register_hitbox=self.register_hitbox,
                x1=cx1, y1=cy1, x2=cx2, y2=cy2
            )
        elif self.current_page == "telemetry":
            page_telemetry.draw_telemetry_page(
                canvas=canvas,
                theme=self.theme,
                profile=self.get_active_profile(),
                controller_count=self.daemon.current_controller_count,
                stick_telemetry=self.daemon.stick_telemetry,
                button_state=self.daemon.button_state,
                register_hitbox=self.register_hitbox,
                x1=cx1, y1=cy1, x2=cx2, y2=cy2
            )
        elif self.current_page == "settings":
            page_settings.draw_settings_page(
                canvas=canvas,
                theme=self.theme,
                cfg=self.cfg,
                is_startup_active=is_windows_startup_enabled(),
                get_launcher_path=lambda k: get_launcher_path(self.cfg, k),
                register_hitbox=self.register_hitbox,
                x1=cx1, y1=cy1, x2=cx2, y2=cy2
            )
        elif self.current_page == "about":
            page_about.draw_about_page(
                canvas=canvas,
                theme=self.theme,
                is_startup_active=is_windows_startup_enabled(),
                uptime_seconds=int(time.time() - self.start_time),
                register_hitbox=self.register_hitbox,
                x1=cx1, y1=cy1, x2=cx2, y2=cy2
            )

    # -------------------------------------------------------------------------
    # In-App Live Hot-Reload Engine
    # -------------------------------------------------------------------------
    def _scan_source_mtimes(self) -> Dict[str, float]:
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        mtimes = {}
        target_dir = os.path.join(root_dir, "hydra_controller")
        for r, _, files in os.walk(target_dir):
            for f in files:
                if f.endswith(".py"):
                    p = os.path.join(r, f)
                    try:
                        mtimes[p] = os.path.getmtime(p)
                    except Exception:
                        pass
        return mtimes

    def _auto_reload_tick(self):
        try:
            current_mtimes = self._scan_source_mtimes()
            changed = False
            for p, mt in current_mtimes.items():
                if p not in self.last_file_mtimes or mt != self.last_file_mtimes[p]:
                    changed = True
                    break
            if changed:
                self.last_file_mtimes = current_mtimes
                importlib.reload(page_dashboard)
                importlib.reload(page_telemetry)
                importlib.reload(page_settings)
                importlib.reload(page_about)
                self.redraw()
                print("[⚡ Hot-Reload] UI modules dynamically reloaded live!")
        except Exception:
            pass
        finally:
            self.after(500, self._auto_reload_tick)

    def _live_heartbeat_tick(self):
        try:
            self.anim_phase = (self.anim_phase + 0.12) % (2 * 3.14159)
            canvas = self.main_canvas

            if self.daemon.is_running:
                import math
                pulse_scale = (math.sin(self.anim_phase) + 1.0) / 2.0  # 0.0 to 1.0
                ring_width = 1.0 + pulse_scale * 2.5
                canvas.itemconfig("daemon_pulse_ring", width=ring_width, outline=self.theme["active_blue_bg"] if pulse_scale > 0.3 else "")
            else:
                canvas.itemconfig("daemon_pulse_ring", outline="")
        except Exception:
            pass
        finally:
            self.after(50, self._live_heartbeat_tick)

    # -------------------------------------------------------------------------
    # Hitbox & Interaction Dispatcher
    # -------------------------------------------------------------------------
    def register_hitbox(self, name: str, x1: float, y1: float, x2: float, y2: float, tooltip: str):
        self.hitboxes[name] = {"bounds": (x1, y1, x2, y2), "tooltip": tooltip}

    def on_canvas_click(self, event):
        x, y = event.x, event.y
        for name, data in self.hitboxes.items():
            bx1, by1, bx2, by2 = data["bounds"]
            if bx1 <= x <= bx2 and by1 <= y <= by2:
                self.handle_action(name)
                return

    def on_canvas_hover(self, event):
        x, y = event.x, event.y
        matched = None
        for name, data in self.hitboxes.items():
            bx1, by1, bx2, by2 = data["bounds"]
            if bx1 <= x <= bx2 and by1 <= y <= by2:
                matched = name
                break

        if matched != self.hovered_hitbox:
            self.hovered_hitbox = matched
            self.main_canvas.config(cursor="hand2" if matched else "")

    def handle_action(self, action_name: str):
        if action_name in ("nav_dashboard", "nav_logo"):
            self.current_page = "dashboard"
            self.redraw()
        elif action_name == "nav_telemetry":
            self.current_page = "telemetry"
            self.redraw()
        elif action_name == "nav_settings":
            self.current_page = "settings"
            self.redraw()
        elif action_name == "nav_about":
            self.current_page = "about"
            self.redraw()
        elif action_name == "about_open_github":
            webbrowser.open("https://github.com/the-jay-code")
        elif action_name == "about_open_hydra_github":
            webbrowser.open("https://github.com/hydralauncher/hydra")
        elif action_name in ("toggle_theme_btn", "toggle_theme_setting"):
            self.toggle_theme()
        elif action_name == "toggle_monitor_state":
            self.toggle_monitor()
        elif action_name == "toggle_startup_reg":
            new_state = not is_windows_startup_enabled()
            set_windows_startup_enabled(new_state)
            self.redraw()
        elif action_name == "toggle_auto_launch":
            self.cfg["auto_launch_on_controller"] = not self.cfg.get("auto_launch_on_controller", True)
            save_config(self.cfg)
            self.redraw()
        elif action_name == "toggle_kill_disc":
            self.cfg["kill_on_disconnect"] = not self.cfg.get("kill_on_disconnect", False)
            save_config(self.cfg)
            self.redraw()
        elif action_name == "toggle_sound_alerts":
            self.cfg["sound_alerts"] = not self.cfg.get("sound_alerts", True)
            self.cfg["toast_notifications"] = self.cfg["sound_alerts"]
            save_config(self.cfg)
            self.redraw()
        elif action_name == "toggle_guide_shortcut":
            self.cfg["guide_shortcut_enabled"] = not self.cfg.get("guide_shortcut_enabled", True)
            save_config(self.cfg)
            self.redraw()
        elif action_name == "toggle_tray_on_close":
            self.cfg["minimize_to_tray"] = not self.cfg.get("minimize_to_tray", False)
            save_config(self.cfg)
            self.redraw()
        elif action_name.startswith("set_target_"):
            target_key = action_name.replace("set_target_", "")
            self.cfg["target_launcher"] = target_key
            save_config(self.cfg)
            self.redraw()
        elif action_name.startswith("browse_launcher_"):
            target_key = action_name.replace("browse_launcher_", "")
            chosen = filedialog.askopenfilename(
                title=f"Select Executable for {target_key.title()}",
                filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")]
            )
            if chosen:
                if "launcher_paths" not in self.cfg:
                    self.cfg["launcher_paths"] = {}
                self.cfg["launcher_paths"][target_key] = chosen
                if target_key == "hydra":
                    self.cfg["custom_hydra_path"] = chosen
                save_config(self.cfg)
                self.redraw()
        elif action_name == "settings_autodetect_all":
            detected_h = find_hydra_exe(self.cfg)
            detected_s = find_steam_exe(self.cfg)
            detected_p = find_playnite_exe(self.cfg)
            if "launcher_paths" not in self.cfg:
                self.cfg["launcher_paths"] = {}
            if detected_h:
                self.cfg["launcher_paths"]["hydra"] = detected_h
            if detected_s:
                self.cfg["launcher_paths"]["steam"] = detected_s
            if detected_p:
                self.cfg["launcher_paths"]["playnite"] = detected_p
            save_config(self.cfg)
            self.redraw()
            messagebox.showinfo("Auto-Discovery Complete", f"Hydra: {detected_h}\nSteam: {detected_s}\nPlaynite: {detected_p}")
        elif action_name == "settings_reset_defaults":
            if messagebox.askyesno("Reset Configuration", "Restore all settings and launcher paths to default?"):
                self.cfg = DEFAULT_CONFIG.copy()
                save_config(self.cfg)
                self.redraw()
        elif action_name == "dash_launch_hydra_btn":
            threading.Thread(target=self.launch_target_app, daemon=True).start()
            self.redraw()
        elif action_name == "dash_rescan_btn":
            self.daemon.check_controllers_fast()
            self.redraw()
        elif action_name == "dash_rumble_test_btn":
            self.daemon.trigger_rumble_test()
        elif action_name == "dash_minimize_tray_btn":
            self.minimize_to_tray()

    # -------------------------------------------------------------------------
    # Controller Profile Classifier
    # -------------------------------------------------------------------------
    def get_active_profile(self) -> Dict[str, Any]:
        if self.daemon.current_controller_count == 0 or not self.daemon.connected_controller_name:
            return {
                "type": "standby",
                "brand": "Standby",
                "display_name": "No Controller Connected",
                "sub": "Connect any Xbox, PlayStation, or Switch gamepad to automatically trigger launcher",
                "battery": "Standby",
                "face_buttons": "STANDBY",
                "badge_bg": self.theme["pill_dark"],
                "badge_fg": self.theme["text_muted"],
                "accent": self.theme["text_muted"],
            }

        name = self.daemon.connected_controller_name
        lower = name.lower()
        batt = self.daemon.battery_status_str

        if any(k in lower for k in ["xbox", "xinput", "microsoft"]):
            return {
                "type": "xbox",
                "brand": "Xbox Gamepad",
                "display_name": name,
                "sub": "Xbox Wireless / XInput • 200Hz Low-Latency Active",
                "battery": batt,
                "face_buttons": "Ⓐ  Ⓑ  Ⓧ  Ⓨ",
                "badge_bg": self.theme["active_blue_bg"],
                "badge_fg": self.theme["active_blue"],
                "accent": self.theme["active_blue"],
            }
        elif any(k in lower for k in ["dualsense", "dualshock", "ps5", "ps4", "playstation", "sony", "wireless controller"]):
            return {
                "type": "playstation",
                "brand": "PlayStation",
                "display_name": name,
                "sub": "DualSense / DualShock • Haptic Dual-Motor Ready",
                "battery": batt,
                "face_buttons": "△  ○  ✕  □",
                "badge_bg": self.theme["active_blue_bg"],
                "badge_fg": self.theme["active_blue"],
                "accent": self.theme["active_blue"],
            }
        elif any(k in lower for k in ["nintendo", "switch", "joy-con", "pro controller"]):
            return {
                "type": "nintendo",
                "brand": "Nintendo Switch",
                "display_name": name,
                "sub": "Switch Pro / Joy-Con • Bluetooth Subsystem Active",
                "battery": batt,
                "face_buttons": "A  B  X  Y",
                "badge_bg": self.theme["active_blue_bg"],
                "badge_fg": self.theme["active_blue"],
                "accent": self.theme["active_blue"],
            }
        else:
            return {
                "type": "generic",
                "brand": "Gamepad",
                "display_name": name,
                "sub": "USB DirectInput Gamepad • Background Monitoring Active",
                "battery": batt,
                "face_buttons": "1  2  3  4",
                "badge_bg": self.theme["active_blue_bg"],
                "badge_fg": self.theme["active_blue"],
                "accent": self.theme["active_blue"],
            }

    def get_target_launcher_name(self) -> str:
        target = self.cfg.get("target_launcher", "hydra")
        names = {
            "hydra": "Hydra Launcher",
            "steam": "Steam Big Picture",
            "playnite": "Playnite Fullscreen",
            "custom": "Custom App"
        }
        return names.get(target, "Hydra Launcher")

    def on_controller_state_change(self, count: int, name: str):
        self.after(0, self.redraw)

    def on_button_update(self, btn_state: Dict[str, Any]):
        if self.current_page == "telemetry":
            self.after(0, self.redraw)

    def on_telemetry_update(self, telemetry: Dict[str, float]):
        if self.current_page == "telemetry":
            self.after(0, self.update_live_telemetry_hud, telemetry)

    def update_live_telemetry_hud(self, tel: Dict[str, float]):
        canvas = self.main_canvas
        meta = getattr(canvas, "telemetry_meta", None)
        try:
            ls_x = tel.get('ls_x', 0.0)
            ls_y = tel.get('ls_y', 0.0)
            rs_x = tel.get('rs_x', 0.0)
            rs_y = tel.get('rs_y', 0.0)
            lt_v = max(0.0, min(1.0, tel.get('lt', 0.0)))
            rt_v = max(0.0, min(1.0, tel.get('rt', 0.0)))

            if meta:
                # 1. Left Stick dot across radar scope
                ls_cx, ls_cy, ls_r = meta["ls_cx"], meta["ls_cy"], meta.get("ls_r", 42)
                ls_px = ls_cx + int(ls_x * (ls_r - 8))
                ls_py = ls_cy + int(ls_y * (ls_r - 8))
                canvas.coords("ls_dot", ls_px - 6, ls_py - 6, ls_px + 6, ls_py + 6)

                # 2. Right Stick dot across radar scope
                rs_cx, rs_cy, rs_r = meta["rs_cx"], meta["rs_cy"], meta.get("rs_r", 42)
                rs_px = rs_cx + int(rs_x * (rs_r - 8))
                rs_py = rs_cy + int(rs_y * (rs_r - 8))
                canvas.coords("rs_dot", rs_px - 6, rs_py - 6, rs_px + 6, rs_py + 6)

                # 3. Dynamic Trigger Bars
                trig_x = meta["trig_x"]
                bar_w = meta["bar_w"]
                lt_fill = max(1, int(bar_w * lt_v))
                rt_fill = max(1, int(bar_w * rt_v))
                lt_y1, lt_y2 = meta.get("lt_y1", 0), meta.get("lt_y2", 0)
                rt_y1, rt_y2 = meta.get("rt_y1", 0), meta.get("rt_y2", 0)
                canvas.coords("lt_bar_fill", trig_x, lt_y1, trig_x + lt_fill, lt_y2)
                canvas.coords("rt_bar_fill", trig_x, rt_y1, trig_x + rt_fill, rt_y2)

            # 4. Update coordinate text readouts
            canvas.itemconfig("ls_text", text=f"Left Stick (LS)\nX: {ls_x:+.2f}  Y: {ls_y:+.2f}")
            canvas.itemconfig("rs_text", text=f"Right Stick (RS)\nX: {rs_x:+.2f}  Y: {rs_y:+.2f}")
            canvas.itemconfig("lt_text", text=f"LT [{int(lt_v * 100)}%]")
            canvas.itemconfig("rt_text", text=f"RT [{int(rt_v * 100)}%]")
        except Exception:
            pass

    def toggle_monitor(self):
        if self.daemon.is_running:
            self.daemon.stop()
        else:
            self.daemon.start()
        self.tray_manager.update_icon(self.daemon.is_running)
        self.redraw()

    def launch_target_app(self):
        launch_target_launcher(self.cfg)

    def kill_target_app(self):
        kill_target_launcher(self.cfg)

    def show_from_tray(self):
        self.after(0, self._restore_window)

    def _bring_to_front(self):
        try:
            self.deiconify()
            self.lift()
            self.attributes("-topmost", True)
            self.after_idle(self.attributes, "-topmost", False)
            self.focus_force()
        except Exception:
            pass

    def _restore_window(self):
        self._bring_to_front()
        self.redraw()

    def minimize_to_tray(self):
        self.withdraw()
        self.tray_manager.update_icon(self.daemon.is_running)

    def on_closing(self):
        if self.cfg.get("minimize_to_tray", False):
            self.minimize_to_tray()
        else:
            self.exit_app()

    def exit_app(self):
        self.daemon.stop()
        self.tray_manager.stop()
        try:
            self.destroy()
        except Exception:
            pass
        os._exit(0)
