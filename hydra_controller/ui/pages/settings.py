import tkinter as tk
from typing import Dict, Any, Callable
from hydra_controller.ui.geometry import draw_rounded_rect


def draw_settings_page(
    canvas: tk.Canvas,
    theme: Dict[str, str],
    cfg: Dict[str, Any],
    is_startup_active: bool,
    get_launcher_path: Callable[[str], str],
    register_hitbox: Callable[[str, float, float, float, float, str], None],
    x1: float, y1: float, x2: float, y2: float
):
    T = theme
    gap = 14
    total_w = x2 - x1
    col_w = (total_w - gap) / 2

    # Header Title
    canvas.create_text(x1 + 4, y1 + 18, anchor="w", text="Settings & Preferences", fill=T["text_light"], font=("Segoe UI", 22, "bold"))
    canvas.create_text(x1 + 4, y1 + 44, anchor="w", text="Configure daemon automation triggers, Windows boot options, and launcher paths.", fill=T["text_muted"], font=("Segoe UI", 12))

    cards_y1 = y1 + 68
    cards_y2 = y2
    card_h = cards_y2 - cards_y1

    # =========================================================================
    # COLUMN 1: AUTOMATION & BOOT INTEGRATION
    # =========================================================================
    c1_x1 = x1
    c1_x2 = c1_x1 + col_w
    draw_rounded_rect(canvas, c1_x1, cards_y1, c1_x2, cards_y2, radius=20, fill=T["card_bg"], outline=T["card_border"], width=1.5)
    canvas.create_text(c1_x1 + 26, cards_y1 + 26, anchor="w", text="Automation & Boot Integration", fill=T["text_light"], font=("Segoe UI", 15, "bold"))

    switches = [
        ("Run on Windows Startup", "Launches daemon silently in system tray on boot", is_startup_active, "toggle_startup_reg"),
        ("Auto-Launch on Connect", "Starts game launcher when a controller connects", cfg.get("auto_launch_on_controller", True), "toggle_auto_launch"),
        ("Kill on Disconnect", "Stops launcher process when all controllers unplug", cfg.get("kill_on_disconnect", False), "toggle_kill_disc"),
        ("Audio Chimes & Toast Alerts", "Plays audio chime & shows toast on connect", cfg.get("sound_alerts", True), "toggle_sound_alerts"),
        ("Guide / Home Shortcut", "Hold Guide or L3+R3 for 1s to focus launcher", cfg.get("guide_shortcut_enabled", True), "toggle_guide_shortcut"),
        ("Minimize to Tray on Close", "Hides to notification area instead of quitting", cfg.get("minimize_to_tray", False), "toggle_tray_on_close"),
    ]

    usable_left_h = card_h - 56 - 58
    num_sw = len(switches)
    row_h = min(70, int((usable_left_h - (num_sw - 1) * 8) / num_sw))
    row_gap = int((usable_left_h - num_sw * row_h) / max(1, num_sw - 1))
    row_gap = max(6, min(12, row_gap))

    sw_y_start = cards_y1 + 52

    for i, (title, subtitle, val, act_id) in enumerate(switches):
        sy = sw_y_start + i * (row_h + row_gap)
        
        # Sub-card item row
        draw_rounded_rect(canvas, c1_x1 + 18, sy, c1_x2 - 18, sy + row_h, radius=12, fill=T["card_hero_bg"], outline=T["card_border"], width=1)
        
        # Labels
        canvas.create_text(c1_x1 + 30, sy + row_h * 0.35, anchor="w", text=title, fill=T["text_light"], font=("Segoe UI", 12, "bold"))
        canvas.create_text(c1_x1 + 30, sy + row_h * 0.68, anchor="w", text=subtitle, fill=T["text_muted"], font=("Segoe UI", 10))
        
        # Switch Pill
        sw_w, sw_h = 44, 22
        sw_x2 = c1_x2 - 30
        sw_x1 = sw_x2 - sw_w
        sw_y1 = sy + (row_h - sw_h) // 2
        sw_y2 = sw_y1 + sw_h
        bg = T["active_blue"] if val else T["pill_dark"]
        draw_rounded_rect(canvas, sw_x1, sw_y1, sw_x2, sw_y2, radius=11, fill=bg, outline=T["outer_border"], width=1)
        
        knob_x = sw_x2 - 11 if val else sw_x1 + 11
        canvas.create_oval(knob_x - 7, sw_y1 + 4, knob_x + 7, sw_y2 - 4, fill=T["pill_light"], outline="")
        register_hitbox(act_id, sw_x1 - 4, sw_y1 - 4, sw_x2 + 4, sw_y2 + 4, f"Toggle {title}")

    # Reset Defaults Footer
    rst_h = 38
    rst_y1 = cards_y2 - rst_h - 16
    rst_y2 = rst_y1 + rst_h
    draw_rounded_rect(canvas, c1_x1 + 18, rst_y1, c1_x2 - 18, rst_y2, radius=10, fill=T["card_hero_bg"], outline=T["card_border"], width=1)
    canvas.create_text((c1_x1 + c1_x2)//2, (rst_y1 + rst_y2)//2, text="↺ Reset All Settings to Defaults", fill=T["text_muted"], font=("Segoe UI", 11, "bold"))
    register_hitbox("settings_reset_defaults", c1_x1 + 18, rst_y1, c1_x2 - 18, rst_y2, "Restore all default configuration values")

    # =========================================================================
    # COLUMN 2: TARGET LAUNCHERS & CUSTOM PATHS
    # =========================================================================
    c2_x1 = c1_x2 + gap
    c2_x2 = x2
    draw_rounded_rect(canvas, c2_x1, cards_y1, c2_x2, cards_y2, radius=20, fill=T["card_bg"], outline=T["card_border"], width=1.5)
    canvas.create_text(c2_x1 + 26, cards_y1 + 26, anchor="w", text="Target Launchers & Custom Paths", fill=T["text_light"], font=("Segoe UI", 15, "bold"))

    active_target = cfg.get("target_launcher", "hydra")
    launchers = [
        ("hydra", "Hydra Launcher", get_launcher_path("hydra")),
        ("steam", "Steam Big Picture", get_launcher_path("steam")),
        ("playnite", "Playnite Fullscreen", get_launcher_path("playnite")),
        ("custom", "Custom Executable / Game", get_launcher_path("custom")),
    ]

    usable_right_h = card_h - 56 - 58
    num_l = len(launchers)
    l_row_h = min(96, int((usable_right_h - (num_l - 1) * 10) / num_l))
    l_row_gap = int((usable_right_h - num_l * l_row_h) / max(1, num_l - 1))
    l_row_gap = max(8, min(14, l_row_gap))

    l_row_y_start = cards_y1 + 52

    for idx, (key, name, path_val) in enumerate(launchers):
        ly = l_row_y_start + idx * (l_row_h + l_row_gap)
        is_active = (active_target == key)
        
        # Row Box
        row_outline = T["active_blue"] if is_active else T["card_border"]
        draw_rounded_rect(canvas, c2_x1 + 18, ly, c2_x2 - 18, ly + l_row_h, radius=14, fill=T["card_hero_bg"], outline=row_outline, width=1.8 if is_active else 1)
        
        # Radio Selector & Title
        radio_text = "●" if is_active else "○"
        canvas.create_text(c2_x1 + 34, ly + 22, anchor="w", text=f"{radio_text}  {name}", fill=T["text_light"], font=("Segoe UI", 13, "bold"))
        
        register_hitbox(f"set_target_{key}", c2_x1 + 18, ly, c2_x2 - 120, ly + 40, f"Select {name} as active launcher")

        # Status Badge on Header Right
        badge_txt = "ACTIVE TARGET" if is_active else ("CUSTOM PATH" if cfg.get("launcher_paths", {}).get(key) else "AUTO-DETECTED")
        badge_bg = T["active_blue_bg"] if is_active else T["pill_dark"]
        badge_fg = T["active_blue"] if is_active else T["text_muted"]
        draw_rounded_rect(canvas, c2_x2 - 135, ly + 10, c2_x2 - 28, ly + 32, radius=8, fill=badge_bg, outline="")
        canvas.create_text(c2_x2 - 81, ly + 21, text=badge_txt, fill=badge_fg, font=("Segoe UI", 8, "bold"))

        # Path Text Bar inside row
        path_display = (path_val[:38] + "...") if len(path_val) > 41 else (path_val if path_val else "Not configured / Auto-detect on launch")
        box_h = 28
        box_y1 = ly + 42
        box_y2 = box_y1 + box_h
        draw_rounded_rect(canvas, c2_x1 + 34, box_y1, c2_x2 - 118, box_y2, radius=6, fill=T["pill_dark"], outline=T["outer_border"], width=1)
        canvas.create_text(c2_x1 + 44, (box_y1 + box_y2)//2, anchor="w", text=path_display, fill=T["active_blue"] if is_active else T["text_muted"], font=("Consolas", 9, "bold"))

        # Browse Button
        btn_bx1 = c2_x2 - 108
        btn_by1 = box_y1
        btn_bx2 = c2_x2 - 28
        btn_by2 = box_y2
        draw_rounded_rect(canvas, btn_bx1, btn_by1, btn_bx2, btn_by2, radius=8, fill=T["pill_light"] if is_active else T["pill_dark"], outline=T["outer_border"], width=1)
        canvas.create_text((btn_bx1 + btn_bx2)//2, (btn_by1 + btn_by2)//2, text="📁 Browse", fill=T["text_dark"] if is_active else T["text_light"], font=("Segoe UI", 10, "bold"))
        register_hitbox(f"browse_launcher_{key}", btn_bx1, btn_by1, btn_bx2, btn_by2, f"Browse custom path for {name}")

    # Auto-Detect All Default Paths Action Bar
    auto_h = 38
    auto_y1 = cards_y2 - auto_h - 16
    auto_y2 = auto_y1 + auto_h
    draw_rounded_rect(canvas, c2_x1 + 18, auto_y1, c2_x2 - 18, auto_y2, radius=10, fill=T["card_hero_bg"], outline=T["active_blue"], width=1.2)
    canvas.create_text((c2_x1 + c2_x2)//2, (auto_y1 + auto_y2)//2, text="⚲ Auto-Detect & Refresh All Launcher Paths", fill=T["active_blue"], font=("Segoe UI", 11, "bold"))
    register_hitbox("settings_autodetect_all", c2_x1 + 18, auto_y1, c2_x2 - 18, auto_y2, "Scan system for Hydra, Steam, and Playnite installations")
