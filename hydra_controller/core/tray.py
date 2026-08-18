import threading
import logging
from typing import Callable, Optional
import pystray
from PIL import Image, ImageDraw

logger = logging.getLogger("hydra_bento")


import os

def create_tray_image(is_running: bool = True) -> Image.Image:
    """Generates a crisp 64x64 system tray icon using app_icon.png."""
    icon_png = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets", "app_icon.png")
    if os.path.exists(icon_png):
        try:
            base_img = Image.open(icon_png).convert("RGBA").resize((64, 64), Image.Resampling.LANCZOS)
            draw = ImageDraw.Draw(base_img)
            # Status dot in bottom right
            dot_col = (34, 197, 94, 255) if is_running else (239, 68, 68, 255)
            draw.ellipse((44, 44, 60, 60), fill=dot_col, outline=(13, 20, 36, 255), width=2)
            return base_img
        except Exception:
            pass

    img = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((4, 4, 60, 60), fill=(24, 26, 33, 255), outline=(56, 189, 248, 255) if is_running else (239, 68, 68, 255), width=3)
    emblem_points = [
        (32, 14), (36, 28), (50, 32), (36, 36),
        (32, 50), (28, 36), (14, 32), (28, 28)
    ]
    draw.polygon(emblem_points, fill=(241, 245, 249, 255))
    return img


class SystemTrayManager:
    def __init__(self, on_open: Callable, on_launch: Callable, on_toggle_mon: Callable, on_exit: Callable):
        self.on_open = on_open
        self.on_launch = on_launch
        self.on_toggle_mon = on_toggle_mon
        self.on_exit = on_exit
        self.tray_icon: Optional[pystray.Icon] = None
        self.is_running = False

    def start(self, daemon_active: bool = True):
        menu = pystray.Menu(
            pystray.MenuItem("Open BP Launcher", lambda icon, item: self.on_open(), default=True),
            pystray.MenuItem("Launch Gamepad Target", lambda icon, item: self.on_launch()),
            pystray.MenuItem("Pause / Resume Monitor", lambda icon, item: self.on_toggle_mon()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit Completely", lambda icon, item: self.on_exit())
        )

        self.tray_icon = pystray.Icon(
            "BPLauncher",
            create_tray_image(daemon_active),
            "BP Launcher (Big Picture Edition)",
            menu=menu
        )

        def _run():
            self.is_running = True
            try:
                self.tray_icon.run()
            except Exception as e:
                logger.error(f"Tray error: {e}")
            finally:
                self.is_running = False

        threading.Thread(target=_run, daemon=True).start()

    def update_icon(self, daemon_active: bool):
        if self.tray_icon:
            self.tray_icon.icon = create_tray_image(daemon_active)

    def show_toast(self, title: str, message: str):
        if self.tray_icon:
            try:
                self.tray_icon.notify(message, title)
            except Exception:
                pass

    def stop(self):
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
