import tkinter as tk
from typing import Dict, Any, Callable
from hydra_controller.ui.geometry import draw_rounded_rect


def draw_telemetry_page(
    canvas: tk.Canvas,
    theme: Dict[str, str],
    profile: Dict[str, Any],
    controller_count: int,
    stick_telemetry: Dict[str, float],
    button_state: Dict[str, Any],
    register_hitbox: Callable[[str, float, float, float, float, str], None],
    x1: float, y1: float, x2: float, y2: float
):
    T = theme
    gap = 14
    total_w = x2 - x1
    total_h = y2 - y1

    # Header
    canvas.create_text(x1 + 4, y1 + 18, anchor="w", text="Hardware Telemetry & Input Lab", fill=T["text_light"], font=("Segoe UI", 22, "bold"))
    canvas.create_text(x1 + 4, y1 + 44, anchor="w", text="Real-time analog stick radar, trigger pressure gauges, and physical button matrix.", fill=T["text_muted"], font=("Segoe UI", 12))

    cards_y1 = y1 + 68
    cards_y2 = y2
    card_h = cards_y2 - cards_y1
    col_w = (total_w - gap) / 2

    # =========================================================================
    # COLUMN 1: ANALOG STICK RADAR HUD
    # =========================================================================
    c1_x1 = x1
    c1_x2 = c1_x1 + col_w
    draw_rounded_rect(canvas, c1_x1, cards_y1, c1_x2, cards_y2, radius=20, fill=T["card_bg"], outline=T["card_border"], width=1.5)
    canvas.create_text(c1_x1 + 26, cards_y1 + 24, anchor="w", text="Precision Thumbstick Radar", fill=T["text_light"], font=("Segoe UI", 15, "bold"))

    # Dual Radar Scope Box
    scope_box_y1 = cards_y1 + 52
    scope_box_y2 = scope_box_y1 + int(card_h * 0.52)
    draw_rounded_rect(canvas, c1_x1 + 18, scope_box_y1, c1_x2 - 18, scope_box_y2, radius=14, fill=T["card_inner_bg"], outline=T["card_border"], width=1)

    scope_mid_y = (scope_box_y1 + scope_box_y2) // 2
    scope_w = (c1_x2 - c1_x1 - 36) / 2

    # Left Stick Scope
    ls_cx = int(c1_x1 + 18 + scope_w * 0.5)
    ls_cy = scope_mid_y
    ls_r = 42

    canvas.create_oval(ls_cx - ls_r, ls_cy - ls_r, ls_cx + ls_r, ls_cy + ls_r, fill=T["pill_dark"], outline=T["card_border"], width=1.5)
    canvas.create_oval(ls_cx - ls_r//2, ls_cy - ls_r//2, ls_cx + ls_r//2, ls_cy + ls_r//2, fill="", outline=T["card_border"], width=1)
    canvas.create_line(ls_cx - ls_r, ls_cy, ls_cx + ls_r, ls_cy, fill=T["card_border"])
    canvas.create_line(ls_cx, ls_cy - ls_r, ls_cx, ls_cy + ls_r, fill=T["card_border"])

    ls_px = ls_cx + int(stick_telemetry.get('ls_x', 0.0) * (ls_r - 8))
    ls_py = ls_cy + int(stick_telemetry.get('ls_y', 0.0) * (ls_r - 8))
    canvas.create_oval(ls_px - 6, ls_py - 6, ls_px + 6, ls_py + 6, fill=T["active_blue"], outline="", tags=("ls_dot",))
    canvas.create_text(ls_cx, scope_box_y2 - 20, text=f"Left Stick (LS)\nX: {stick_telemetry.get('ls_x', 0.0):+.2f}  Y: {stick_telemetry.get('ls_y', 0.0):+.2f}", fill=T["text_muted"], font=("Consolas", 9, "bold"), tags=("ls_text",), justify="center")

    # Right Stick Scope
    rs_cx = int(c1_x1 + 18 + scope_w * 1.5)
    rs_cy = scope_mid_y
    rs_r = 42

    canvas.create_oval(rs_cx - rs_r, rs_cy - rs_r, rs_cx + rs_r, rs_cy + rs_r, fill=T["pill_dark"], outline=T["card_border"], width=1.5)
    canvas.create_oval(rs_cx - rs_r//2, rs_cy - rs_r//2, rs_cx + rs_r//2, rs_cy + rs_r//2, fill="", outline=T["card_border"], width=1)
    canvas.create_line(rs_cx - rs_r, rs_cy, rs_cx + rs_r, rs_cy, fill=T["card_border"])
    canvas.create_line(rs_cx, rs_cy - rs_r, rs_cx, rs_cy + rs_r, fill=T["card_border"])

    rs_px = rs_cx + int(stick_telemetry.get('rs_x', 0.0) * (rs_r - 8))
    rs_py = rs_cy + int(stick_telemetry.get('rs_y', 0.0) * (rs_r - 8))
    canvas.create_oval(rs_px - 6, rs_py - 6, rs_px + 6, rs_py + 6, fill=T["accent_purple"], outline="", tags=("rs_dot",))
    canvas.create_text(rs_cx, scope_box_y2 - 20, text=f"Right Stick (RS)\nX: {stick_telemetry.get('rs_x', 0.0):+.2f}  Y: {stick_telemetry.get('rs_y', 0.0):+.2f}", fill=T["text_muted"], font=("Consolas", 9, "bold"), tags=("rs_text",), justify="center")

    # Trigger Gauges Box
    trig_box_y1 = scope_box_y2 + 12
    trig_box_y2 = cards_y2 - 62
    draw_rounded_rect(canvas, c1_x1 + 18, trig_box_y1, c1_x2 - 18, trig_box_y2, radius=14, fill=T["card_inner_bg"], outline=T["card_border"], width=1)

    trig_mid_y = (trig_box_y1 + trig_box_y2) // 2
    trig_bar_w = int(c1_x2 - c1_x1 - 180)
    trig_x = c1_x1 + 36

    canvas.create_text(trig_x, trig_mid_y - 14, anchor="w", text=f"LT [{int(stick_telemetry.get('lt', 0.0)*100)}%]", fill=T["text_light"], font=("Consolas", 10, "bold"), tags=("lt_text",))
    canvas.create_text(trig_x, trig_mid_y + 14, anchor="w", text=f"RT [{int(stick_telemetry.get('rt', 0.0)*100)}%]", fill=T["text_light"], font=("Consolas", 10, "bold"), tags=("rt_text",))

    # LT Bar
    draw_rounded_rect(canvas, trig_x + 90, trig_mid_y - 20, trig_x + 90 + trig_bar_w, trig_mid_y - 8, radius=4, fill=T["pill_dark"], outline="")
    lt_fill = max(1, int(trig_bar_w * stick_telemetry.get('lt', 0.0)))
    canvas.create_rectangle(trig_x + 90, trig_mid_y - 20, trig_x + 90 + lt_fill, trig_mid_y - 8, fill=T["active_blue"] if stick_telemetry.get('lt', 0.0) > 0 else T["pill_dark"], outline="", tags=("lt_bar_fill",))

    # RT Bar
    draw_rounded_rect(canvas, trig_x + 90, trig_mid_y + 8, trig_x + 90 + trig_bar_w, trig_mid_y + 20, radius=4, fill=T["pill_dark"], outline="")
    rt_fill = max(1, int(trig_bar_w * stick_telemetry.get('rt', 0.0)))
    canvas.create_rectangle(trig_x + 90, trig_mid_y + 8, trig_x + 90 + rt_fill, trig_mid_y + 20, fill=T["accent_purple"] if stick_telemetry.get('rt', 0.0) > 0 else T["pill_dark"], outline="", tags=("rt_bar_fill",))

    # Store telemetry coordinates for fast real-time in-place updates
    canvas.telemetry_meta = {
        'ls_cx': ls_cx,
        'ls_cy': ls_cy,
        'ls_r': ls_r,
        'rs_cx': rs_cx,
        'rs_cy': rs_cy,
        'rs_r': rs_r,
        'trig_x': trig_x + 90,
        'bar_w': trig_bar_w,
        'lt_y1': trig_mid_y - 20,
        'lt_y2': trig_mid_y - 8,
        'rt_y1': trig_mid_y + 8,
        'rt_y2': trig_mid_y + 20,
    }

    # Haptic Rumble Test Pulse Button
    rumble_y1 = cards_y2 - 50
    rumble_h = 38
    draw_rounded_rect(canvas, c1_x1 + 18, rumble_y1, c1_x2 - 18, rumble_y1 + rumble_h, radius=10, fill=T["card_hero_bg"], outline=T["accent_purple"], width=1.5)
    canvas.create_text((c1_x1 + c1_x2)//2, rumble_y1 + rumble_h//2, text="💥 Test Controller Haptic Rumble (500ms)", fill=T["accent_purple"], font=("Segoe UI", 11, "bold"))
    register_hitbox("dash_rumble_test_btn", c1_x1 + 18, rumble_y1, c1_x2 - 18, rumble_y1 + rumble_h, "Send 500ms haptic vibration pulse")

    # =========================================================================
    # COLUMN 2: HARDWARE BUTTON MATRIX & INPUT LOG
    # =========================================================================
    c2_x1 = c1_x2 + gap
    c2_x2 = x2
    draw_rounded_rect(canvas, c2_x1, cards_y1, c2_x2, cards_y2, radius=20, fill=T["card_bg"], outline=T["card_border"], width=1.5)
    canvas.create_text(c2_x1 + 26, cards_y1 + 24, anchor="w", text="Live Physical Button Matrix", fill=T["text_light"], font=("Segoe UI", 15, "bold"))

    pressed_btns = button_state.get("pressed_buttons", [])
    buttons_layout = [
        ("Button 0 (A / ✕)", 0),
        ("Button 1 (B / ○)", 1),
        ("Button 2 (X / □)", 2),
        ("Button 3 (Y / △)", 3),
        ("Left Bumper (LB)", 4),
        ("Right Bumper (RB)", 5),
        ("Back / Select", 6),
        ("Start / Options", 7),
        ("Left Stick Click (L3)", 8),
        ("Right Stick Click (R3)", 9),
        ("Guide / Home", 10),
    ]

    btn_grid_y1 = cards_y1 + 52
    row_h = 32
    for idx, (label, btn_idx) in enumerate(buttons_layout):
        by = btn_grid_y1 + idx * (row_h + 6)
        is_pressed = (btn_idx in pressed_btns)
        
        chip_bg = T["active_blue"] if is_pressed else T["card_hero_bg"]
        chip_fg = T["text_dark"] if is_pressed else T["text_muted"]
        chip_border = T["active_blue"] if is_pressed else T["card_border"]

        draw_rounded_rect(canvas, c2_x1 + 20, by, c2_x2 - 20, by + row_h, radius=8, fill=chip_bg, outline=chip_border, width=1.2)
        canvas.create_text(c2_x1 + 34, by + row_h//2, anchor="w", text=label, fill=chip_fg, font=("Segoe UI", 11, "bold"))
        status_str = "PRESSED" if is_pressed else "RELEASED"
        canvas.create_text(c2_x2 - 34, by + row_h//2, anchor="e", text=status_str, fill=chip_fg, font=("Segoe UI", 9, "bold"))
