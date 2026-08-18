import tkinter as tk
from typing import Dict, Any, Callable
from hydra_controller.ui.geometry import draw_rounded_rect


def draw_about_page(
    canvas: tk.Canvas,
    theme: Dict[str, str],
    is_startup_active: bool,
    uptime_seconds: int,
    register_hitbox: Callable[[str, float, float, float, float, str], None],
    x1: float, y1: float, x2: float, y2: float
):
    T = theme
    gap = 14
    total_h = y2 - y1

    hero_h = int(total_h * 0.44)
    bottom_h = total_h - hero_h - gap

    # =========================================================================
    # A. TOP HERO BRANDING CARD
    # =========================================================================
    hx1, hy1, hx2, hy2 = x1, y1, x2, y1 + hero_h
    draw_rounded_rect(canvas, hx1, hy1, hx2, hy2, radius=20, fill=T["card_hero_bg"], outline=T["card_hero_border"], width=1.5)

    # Monogram Emblem
    em_size = 68
    em_x = hx1 + 32
    em_y = hy1 + (hero_h - em_size) // 2
    draw_rounded_rect(canvas, em_x, em_y, em_x + em_size, em_y + em_size, radius=18, fill=T["card_bg"], outline=T["active_blue"], width=2)
    canvas.create_text(em_x + em_size//2, em_y + em_size//2 - 1, text="BP", fill=T["active_blue"], font=("Segoe UI Variable Display", 24, "bold"))

    # Typography
    info_x = em_x + em_size + 24
    canvas.create_text(info_x, em_y + 10, anchor="w", text="BP Launcher", fill=T["text_light"], font=("Segoe UI", 24, "bold"))
    canvas.create_text(info_x, em_y + 36, anchor="w", text="v2.4.0 • Big Picture Edition — Zero-Resource Gamepad Daemon", fill=T["active_blue"], font=("Segoe UI", 12, "bold"))
    canvas.create_text(info_x, em_y + 58, anchor="w", text="Designed to monitor gamepad hotplug events and automate game launchers with 0% idle overhead.", fill=T["text_muted"], font=("Segoe UI", 11))

    # =========================================================================
    # B. BOTTOM DUAL BENTO CARDS
    # =========================================================================
    b_y1 = hy2 + gap
    b_y2 = y2
    b_col_w = (x2 - x1 - gap) / 2

    # CARD 1: DEVELOPER & REPOSITORIES
    b1_x1 = x1
    b1_x2 = b1_x1 + b_col_w
    draw_rounded_rect(canvas, b1_x1, b_y1, b1_x2, b_y2, radius=20, fill=T["card_bg"], outline=T["card_border"], width=1.5)
    canvas.create_text(b1_x1 + 26, b_y1 + 24, anchor="w", text="Developer & Open Source", fill=T["text_light"], font=("Segoe UI", 15, "bold"))

    # Button 1: Developer Profile (@the-jay-code)
    gh_dev_y1 = b_y1 + 54
    gh_dev_h = 42
    draw_rounded_rect(canvas, b1_x1 + 20, gh_dev_y1, b1_x2 - 20, gh_dev_y1 + gh_dev_h, radius=12, fill=T["pill_light"], outline="")
    canvas.create_text((b1_x1 + b1_x2)//2, gh_dev_y1 + gh_dev_h//2, text="↗ Developer Profile (@the-jay-code)", fill=T["text_dark"], font=("Segoe UI", 12, "bold"))
    register_hitbox("about_open_github", b1_x1 + 20, gh_dev_y1, b1_x2 - 20, gh_dev_y1 + gh_dev_h, "Open https://github.com/the-jay-code")

    # Button 2: Official Hydra Launcher GitHub
    gh_hydra_y1 = gh_dev_y1 + gh_dev_h + 12
    gh_hydra_h = 42
    draw_rounded_rect(canvas, b1_x1 + 20, gh_hydra_y1, b1_x2 - 20, gh_hydra_y1 + gh_hydra_h, radius=12, fill=T["card_hero_bg"], outline=T["active_blue"], width=1.5)
    canvas.create_text((b1_x1 + b1_x2)//2, gh_hydra_y1 + gh_hydra_h//2, text="Official Hydra Launcher GitHub", fill=T["active_blue"], font=("Segoe UI", 12, "bold"))
    register_hitbox("about_open_hydra_github", b1_x1 + 20, gh_hydra_y1, b1_x2 - 20, gh_hydra_y1 + gh_hydra_h, "Open https://github.com/hydralauncher/hydra")

    canvas.create_text((b1_x1 + b1_x2)//2, gh_hydra_y1 + gh_hydra_h + 22, text="github.com/hydralauncher/hydra • MIT License", fill=T["text_muted"], font=("Segoe UI", 10))

    # CARD 2: ENGINE SPECS
    b2_x1 = b1_x2 + gap
    b2_x2 = x2
    draw_rounded_rect(canvas, b2_x1, b_y1, b2_x2, b_y2, radius=20, fill=T["card_bg"], outline=T["card_border"], width=1.5)
    canvas.create_text(b2_x1 + 26, b_y1 + 24, anchor="w", text="Engine Specifications", fill=T["text_light"], font=("Segoe UI", 15, "bold"))

    specs = [
        ("Core Engine", "Python 3.12 + Pygame 2.6.1"),
        ("UI Architecture", "CustomTkinter + Modular Bento Vector Canvas"),
        ("System Tray", "pystray + Background Service Active"),
        ("Windows Boot", "Enabled" if is_startup_active else "Disabled"),
        ("Resource Overhead", "0.0% Idle CPU Utilization"),
        ("Session Uptime", f"{uptime_seconds}s active"),
    ]
    for idx, (label, val) in enumerate(specs):
        sy = b_y1 + 54 + idx * 28
        canvas.create_text(b2_x1 + 24, sy, anchor="w", text=label, fill=T["text_muted"], font=("Segoe UI", 11))
        canvas.create_text(b2_x2 - 24, sy, anchor="e", text=val, fill=T["text_light"], font=("Segoe UI", 11, "bold"))
