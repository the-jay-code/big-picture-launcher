import tkinter as tk
from typing import Dict, Any, Callable
from hydra_controller.ui.geometry import draw_rounded_rect


def draw_dashboard_page(
    canvas: tk.Canvas,
    theme: Dict[str, str],
    profile: Dict[str, Any],
    is_running: bool,
    target_name: str,
    controller_count: int,
    stick_telemetry: Dict[str, float],
    register_hitbox: Callable[[str, float, float, float, float, str], None],
    x1: float, y1: float, x2: float, y2: float
):
    T = theme
    total_h = y2 - y1
    gap = 14

    hero_h = int(total_h * 0.50)
    bottom_h = total_h - hero_h - gap

    # =========================================================================
    # A. TOP HERO BENTO CARD
    # =========================================================================
    hx1, hy1, hx2, hy2 = x1, y1, x2, y1 + hero_h
    draw_rounded_rect(canvas, hx1, hy1, hx2, hy2, radius=20, fill=T["card_hero_bg"], outline=T["card_hero_border"], width=1.5)

    # Top Tag
    draw_rounded_rect(canvas, hx1 + 28, hy1 + 20, hx1 + 180, hy1 + 46, radius=13, fill=T["pill_dark"], outline=T["card_border"], width=1)
    canvas.create_text(hx1 + 104, hy1 + 33, text="BIG PICTURE ENGINE", fill=T["active_blue"], font=("Segoe UI", 10, "bold"))

    # Active daemon status indicator
    status_label = "● ACTIVE DAEMON" if is_running else "● MONITOR PAUSED"
    status_col = T["active_blue"] if is_running else T["danger_red"]
    canvas.create_text(hx2 - 28, hy1 + 33, anchor="e", text=status_label, fill=status_col, font=("Segoe UI", 11, "bold"))

    # Main Title
    canvas.create_text(hx1 + 28, hy1 + 74, anchor="w", text="BP Launcher", fill=T["text_light"], font=("Segoe UI", 24, "bold"))

    # Target launcher badge beside title
    draw_rounded_rect(canvas, hx2 - 210, hy1 + 60, hx2 - 28, hy1 + 88, radius=14, fill=T["pill_dark"], outline=T["active_blue"], width=1.2)
    canvas.create_text(hx2 - 119, hy1 + 74, text=f"Target: {target_name}", fill=T["active_blue"], font=("Segoe UI", 11, "bold"))

    # Controller Device Showcase Card inside Hero
    c_box_y1 = hy1 + 102
    c_box_y2 = hy2 - 20
    draw_rounded_rect(canvas, hx1 + 28, c_box_y1, hx2 - 28, c_box_y2, radius=16, fill=T["card_bg"], outline=T["card_border"], width=1.5)

    em_cy = (c_box_y1 + c_box_y2) // 2
    emblem_r = 30
    em_cx = hx1 + 28 + 50

    # Glowing Controller Emblem Circle
    draw_rounded_rect(canvas, em_cx - emblem_r, em_cy - emblem_r, em_cx + emblem_r, em_cy + emblem_r, radius=16, fill=profile["badge_bg"], outline=profile["accent"], width=1.8)
    canvas.create_text(em_cx, em_cy, text="🎮", fill=profile["badge_fg"], font=("Segoe UI Symbol", 24))

    # Controller Details Typography
    text_x = em_cx + emblem_r + 20
    canvas.create_text(text_x, em_cy - 14, anchor="w", text=profile["display_name"], fill=T["text_light"], font=("Segoe UI", 17, "bold"))
    
    batt_str = f" • Battery: {profile['battery']}" if controller_count > 0 else ""
    canvas.create_text(text_x, em_cy + 14, anchor="w", text=f"{profile['sub']}{batt_str}", fill=T["text_muted"], font=("Segoe UI", 12))

    # Face Buttons Pill
    if controller_count > 0:
        fb_w = 120
        fb_x2 = hx2 - 180
        fb_x1 = fb_x2 - fb_w
        draw_rounded_rect(canvas, fb_x1, em_cy - 16, fb_x2, em_cy + 16, radius=10, fill=T["pill_dark"], outline=T["card_border"], width=1)
        canvas.create_text((fb_x1 + fb_x2)//2, em_cy, text=profile["face_buttons"], fill=profile["accent"], font=("Segoe UI Symbol", 11, "bold"))

    # Connection Badge on Right
    c_status_w = 128
    c_status_h = 34
    cs_x2 = hx2 - 44
    cs_x1 = cs_x2 - c_status_w
    cs_y1 = em_cy - c_status_h // 2
    cs_y2 = cs_y1 + c_status_h
    
    badge_title = "CONNECTED" if controller_count > 0 else "STANDBY"
    draw_rounded_rect(canvas, cs_x1, cs_y1, cs_x2, cs_y2, radius=12, fill=profile["badge_bg"], outline=profile["accent"], width=1.2)
    canvas.create_text((cs_x1 + cs_x2)//2, (cs_y1 + cs_y2)//2, text=f"● {badge_title}", fill=profile["badge_fg"], font=("Segoe UI", 11, "bold"))

    # =========================================================================
    # B. BOTTOM DUAL BENTO CARDS
    # =========================================================================
    b_y1 = hy2 + gap
    b_y2 = y2
    b_col_w = (x2 - x1 - gap) / 2

    # CARD 1: STICK & TRIGGER TELEMETRY
    b1_x1 = x1
    b1_x2 = b1_x1 + b_col_w
    draw_rounded_rect(canvas, b1_x1, b_y1, b1_x2, b_y2, radius=20, fill=T["card_bg"], outline=T["card_border"], width=1.5)
    canvas.create_text(b1_x1 + 24, b_y1 + 22, anchor="w", text="Live Stick & Trigger Telemetry", fill=T["text_light"], font=("Segoe UI", 15, "bold"))

    # Telemetry HUD Box
    hud_y1 = b_y1 + 46
    hud_y2 = b_y2 - 64
    draw_rounded_rect(canvas, b1_x1 + 18, hud_y1, b1_x2 - 18, hud_y2, radius=14, fill=T["card_inner_bg"], outline=T["card_border"], width=1)

    # Left Stick Scope
    ls_cx = b1_x1 + 68
    ls_cy = (hud_y1 + hud_y2) // 2
    ls_r = 24
    canvas.create_oval(ls_cx - ls_r, ls_cy - ls_r, ls_cx + ls_r, ls_cy + ls_r, fill=T["pill_dark"], outline=T["card_border"], width=1.5)
    canvas.create_line(ls_cx - ls_r, ls_cy, ls_cx + ls_r, ls_cy, fill=T["card_border"])
    canvas.create_line(ls_cx, ls_cy - ls_r, ls_cx, ls_cy + ls_r, fill=T["card_border"])
    
    ls_px = ls_cx + int(stick_telemetry['ls_x'] * 16)
    ls_py = ls_cy + int(stick_telemetry['ls_y'] * 16)
    canvas.create_oval(ls_px - 5, ls_py - 5, ls_px + 5, ls_py + 5, fill=T["active_blue"], outline="")
    canvas.create_text(ls_cx + 34, ls_cy, anchor="w", text=f"LS Stick\nX: {stick_telemetry['ls_x']:+.2f}\nY: {stick_telemetry['ls_y']:+.2f}", fill=T["text_muted"], font=("Consolas", 9, "bold"))

    # Right Stick Scope
    rs_cx = b1_x1 + 205
    rs_cy = ls_cy
    rs_r = 24
    canvas.create_oval(rs_cx - rs_r, rs_cy - rs_r, rs_cx + rs_r, rs_cy + rs_r, fill=T["pill_dark"], outline=T["card_border"], width=1.5)
    canvas.create_line(rs_cx - rs_r, rs_cy, rs_cx + rs_r, rs_cy, fill=T["card_border"])
    canvas.create_line(rs_cx, rs_cy - rs_r, rs_cx, rs_cy + rs_r, fill=T["card_border"])
    
    rs_px = rs_cx + int(stick_telemetry['rs_x'] * 16)
    rs_py = rs_cy + int(stick_telemetry['rs_y'] * 16)
    canvas.create_oval(rs_px - 5, rs_py - 5, rs_px + 5, rs_py + 5, fill=T["accent_purple"], outline="")
    canvas.create_text(rs_cx + 34, rs_cy, anchor="w", text=f"RS Stick\nX: {stick_telemetry['rs_x']:+.2f}\nY: {stick_telemetry['rs_y']:+.2f}", fill=T["text_muted"], font=("Consolas", 9, "bold"))

    # Trigger Gauges (LT & RT)
    trig_x = b1_x2 - 150
    canvas.create_text(trig_x, ls_cy - 14, anchor="w", text=f"LT [{int(stick_telemetry['lt']*100)}%]", fill=T["text_muted"], font=("Consolas", 10, "bold"))
    canvas.create_text(trig_x, ls_cy + 14, anchor="w", text=f"RT [{int(stick_telemetry['rt']*100)}%]", fill=T["text_muted"], font=("Consolas", 10, "bold"))
    
    bar_w = 65
    # LT Bar
    draw_rounded_rect(canvas, trig_x + 62, ls_cy - 20, trig_x + 62 + bar_w, ls_cy - 8, radius=4, fill=T["pill_dark"], outline="")
    lt_fill = int(bar_w * stick_telemetry['lt'])
    if lt_fill > 0:
        draw_rounded_rect(canvas, trig_x + 62, ls_cy - 20, trig_x + 62 + lt_fill, ls_cy - 8, radius=4, fill=T["active_blue"], outline="")
    
    # RT Bar
    draw_rounded_rect(canvas, trig_x + 62, ls_cy + 8, trig_x + 62 + bar_w, ls_cy + 20, radius=4, fill=T["pill_dark"], outline="")
    rt_fill = int(bar_w * stick_telemetry['rt'])
    if rt_fill > 0:
        draw_rounded_rect(canvas, trig_x + 62, ls_cy + 8, trig_x + 62 + rt_fill, ls_cy + 20, radius=4, fill=T["accent_purple"], outline="")

    # Rumble Vibration Test Button
    rumble_w = (b1_x2 - b1_x1 - 48 - 12) / 2
    rumble_y1 = b_y2 - 50
    rumble_h = 38

    draw_rounded_rect(canvas, b1_x1 + 18, rumble_y1, b1_x1 + 18 + rumble_w, rumble_y1 + rumble_h, radius=10, fill=T["pill_dark"], outline=T["accent_purple"], width=1.5)
    canvas.create_text(b1_x1 + 18 + rumble_w//2, rumble_y1 + rumble_h//2, text="Test Rumble", fill=T["accent_purple"], font=("Segoe UI", 11, "bold"))
    register_hitbox("dash_rumble_test_btn", b1_x1 + 18, rumble_y1, b1_x1 + 18 + rumble_w, rumble_y1 + rumble_h, "Send 500ms haptic vibration pulse")

    # Guide Shortcut Info
    draw_rounded_rect(canvas, b1_x1 + 30 + rumble_w, rumble_y1, b1_x2 - 18, rumble_y1 + rumble_h, radius=10, fill=T["card_inner_bg"], outline=T["card_border"], width=1)
    canvas.create_text((b1_x1 + 30 + rumble_w + b1_x2 - 18)//2, rumble_y1 + rumble_h//2, text="Guide / L3+R3: Focus", fill=T["text_muted"], font=("Segoe UI", 10, "bold"))

    # CARD 2: LAUNCH & PROFILE ACTIONS
    b2_x1 = b1_x2 + gap
    b2_x2 = x2
    draw_rounded_rect(canvas, b2_x1, b_y1, b2_x2, b_y2, radius=20, fill=T["card_bg"], outline=T["card_border"], width=1.5)
    canvas.create_text(b2_x1 + 24, b_y1 + 22, anchor="w", text="Launch & Profile Actions", fill=T["text_light"], font=("Segoe UI", 15, "bold"))

    # Launch Button
    btn_w = (b2_x2 - b2_x1 - 48 - 12) / 2
    btn_h = 44
    btn1_x1 = b2_x1 + 18
    btn1_y1 = b_y1 + 52
    btn1_x2 = btn1_x1 + btn_w
    btn1_y2 = btn1_y1 + btn_h

    draw_rounded_rect(canvas, btn1_x1, btn1_y1, btn1_x2, btn1_y2, radius=12, fill=T["pill_light"], outline="")
    canvas.create_text((btn1_x1 + btn1_x2)//2, (btn1_y1 + btn1_y2)//2, text=f"Launch {target_name}", fill=T["text_dark"], font=("Segoe UI", 12, "bold"))
    register_hitbox("dash_launch_hydra_btn", btn1_x1, btn1_y1, btn1_x2, btn1_y2, f"Launch {target_name}")

    # Rescan Button
    btn2_x1 = btn1_x2 + 12
    btn2_y1 = btn1_y1
    btn2_x2 = btn2_x1 + btn_w
    btn2_y2 = btn1_y2

    draw_rounded_rect(canvas, btn2_x1, btn2_y1, btn2_x2, btn2_y2, radius=12, fill=T["pill_dark"], outline=T["card_border"], width=1.5)
    canvas.create_text((btn2_x1 + btn2_x2)//2, (btn2_y1 + btn2_y2)//2, text="↻ Rescan Gamepads", fill=T["text_light"], font=("Segoe UI", 12, "bold"))
    register_hitbox("dash_rescan_btn", btn2_x1, btn2_y1, btn2_x2, btn2_y2, "Force Probing for Connected Gamepads")

    # Minimize to Tray Button
    min_y1 = b_y2 - 50
    draw_rounded_rect(canvas, b2_x1 + 18, min_y1, b2_x2 - 18, min_y1 + 38, radius=10, fill=T["card_inner_bg"], outline=T["card_border"], width=1)
    canvas.create_text((b2_x1 + b2_x2)//2, min_y1 + 19, text="⬇ Minimize to System Tray", fill=T["active_blue"], font=("Segoe UI", 11, "bold"))
    register_hitbox("dash_minimize_tray_btn", b2_x1 + 18, min_y1, b2_x2 - 18, min_y1 + 38, "Hide window to system tray")
