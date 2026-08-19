import tkinter as tk
from typing import Dict, Any, Callable, List
from hydra_controller.ui.geometry import draw_rounded_rect


def draw_dashboard_page(
    canvas: tk.Canvas,
    theme: Dict[str, str],
    profile: Dict[str, Any],
    is_running: bool,
    target_name: str,
    controller_count: int,
    connected_controllers: List[Dict[str, Any]],
    register_hitbox: Callable[[str, float, float, float, float, str], None],
    x1: float, y1: float, x2: float, y2: float
):
    T = theme
    gap = 14
    total_w = x2 - x1
    total_h = y2 - y1

    # Header
    canvas.create_text(x1 + 4, y1 + 18, anchor="w", text="Connected Gamepads", fill=T["text_light"], font=("Segoe UI", 22, "bold"))
    canvas.create_text(x1 + 4, y1 + 44, anchor="w", text="Active gamepad devices, hardware status, and launcher automation.", fill=T["text_muted"], font=("Segoe UI", 12))

    # Connection Status Counter Badge in Header Right
    badge_txt = f"● {controller_count} CONNECTED" if controller_count > 0 else "● STANDBY"
    badge_bg = T["active_blue_bg"] if controller_count > 0 else T["pill_dark"]
    badge_fg = T["active_blue"] if controller_count > 0 else T["text_muted"]
    draw_rounded_rect(canvas, x2 - 140, y1 + 12, x2 - 8, y1 + 42, radius=15, fill=badge_bg, outline="")
    canvas.create_text(x2 - 74, y1 + 27, text=badge_txt, fill=badge_fg, font=("Segoe UI", 10, "bold"))

    content_y1 = y1 + 68
    actions_h = 76
    actions_y1 = y2 - actions_h
    actions_y2 = y2
    cards_area_h = actions_y1 - content_y1 - gap

    # =========================================================================
    # A. CONNECTED CONTROLLERS DISPLAY AREA
    # =========================================================================
    if controller_count == 0:
        # Standby Hero Card
        draw_rounded_rect(canvas, x1, content_y1, x2, actions_y1, radius=20, fill=T["card_bg"], outline=T["card_border"], width=1.5)
        
        mid_cx = (x1 + x2) // 2
        mid_cy = (content_y1 + actions_y1) // 2

        # Standby Icon Circle
        draw_rounded_rect(canvas, mid_cx - 40, mid_cy - 70, mid_cx + 40, mid_cy + 10, radius=24, fill=T["card_hero_bg"], outline=T["card_border"], width=1.5)
        canvas.create_text(mid_cx, mid_cy - 30, text="🎮", fill=T["text_muted"], font=("Segoe UI Symbol", 28))

        canvas.create_text(mid_cx, mid_cy + 34, text="No Gamepads Connected", fill=T["text_light"], font=("Segoe UI", 18, "bold"))
        canvas.create_text(mid_cx, mid_cy + 62, text="Connect an Xbox, PlayStation, or Switch controller via USB or Bluetooth.\nThe launcher will automatically detect and trigger your configured game platform.", fill=T["text_muted"], font=("Segoe UI", 12), justify="center")
    
    else:
        # Show Connected Controller Cards
        num_cards = min(4, max(1, len(connected_controllers)))
        card_h = int((cards_area_h - (num_cards - 1) * gap) / num_cards)
        card_h = max(110, min(180, card_h))

        for idx, ctrl in enumerate(connected_controllers[:4]):
            cy_start = content_y1 + idx * (card_h + gap)
            cy_end = cy_start + card_h

            draw_rounded_rect(canvas, x1, cy_start, x2, cy_end, radius=18, fill=T["card_hero_bg"], outline=T["card_hero_border"], width=1.5)

            # Slot Badge (P1, P2, P3, P4)
            p_badge_size = 56
            p_bx1 = x1 + 24
            p_by1 = cy_start + (card_h - p_badge_size) // 2
            draw_rounded_rect(canvas, p_bx1, p_by1, p_bx1 + p_badge_size, p_by1 + p_badge_size, radius=16, fill=T["card_bg"], outline=T["active_blue"], width=2)
            canvas.create_text(p_bx1 + p_badge_size//2, p_by1 + p_badge_size//2, text=f"P{idx+1}", fill=T["active_blue"], font=("Segoe UI", 16, "bold"))

            # Controller Info
            info_x = p_bx1 + p_badge_size + 24
            c_name = ctrl.get("name", "Gamepad")
            canvas.create_text(info_x, cy_start + card_h * 0.32, anchor="w", text=c_name, fill=T["text_light"], font=("Segoe UI", 16, "bold"))
            
            sub_info = f"{ctrl.get('battery', '🔋 Connected')} • {ctrl.get('num_axes', 6)} Axes • {ctrl.get('num_buttons', 16)} Buttons • 200Hz Low-Latency Active"
            canvas.create_text(info_x, cy_start + card_h * 0.68, anchor="w", text=sub_info, fill=T["text_muted"], font=("Segoe UI", 11))

            # Status Badge on Card Right
            status_x2 = x2 - 28
            status_w = 110
            status_h = 32
            status_y = cy_start + (card_h - status_h) // 2
            draw_rounded_rect(canvas, status_x2 - status_w, status_y, status_x2, status_y + status_h, radius=10, fill=T["active_blue_bg"], outline="")
            canvas.create_text(status_x2 - status_w//2, status_y + status_h//2, text="● ACTIVE", fill=T["active_blue"], font=("Segoe UI", 10, "bold"))

    # =========================================================================
    # B. BOTTOM ACTIONS BAR
    # =========================================================================
    draw_rounded_rect(canvas, x1, actions_y1, x2, actions_y2, radius=16, fill=T["card_bg"], outline=T["card_border"], width=1.2)

    btn_count = 3
    btn_gap = 12
    btn_w = (total_w - 36 - (btn_count - 1) * btn_gap) / btn_count
    btn_h = 44
    btn_y1 = actions_y1 + (actions_h - btn_h) // 2
    btn_y2 = btn_y1 + btn_h

    # 1. Launch Game Launcher Button
    b1_x1 = x1 + 18
    b1_x2 = b1_x1 + btn_w
    draw_rounded_rect(canvas, b1_x1, btn_y1, b1_x2, btn_y2, radius=12, fill=T["pill_light"], outline="")
    canvas.create_text((b1_x1 + b1_x2)//2, (btn_y1 + btn_y2)//2, text=f"🚀 Launch {target_name}", fill=T["text_dark"], font=("Segoe UI", 12, "bold"))
    register_hitbox("dash_launch_hydra_btn", b1_x1, btn_y1, b1_x2, btn_y2, f"Launch {target_name}")

    # 2. Rescan Controllers Button
    b2_x1 = b1_x2 + btn_gap
    b2_x2 = b2_x1 + btn_w
    draw_rounded_rect(canvas, b2_x1, btn_y1, b2_x2, btn_y2, radius=12, fill=T["card_hero_bg"], outline=T["active_blue"], width=1.2)
    canvas.create_text((b2_x1 + b2_x2)//2, (btn_y1 + btn_y2)//2, text="⟳ Rescan Connected Controllers", fill=T["active_blue"], font=("Segoe UI", 12, "bold"))
    register_hitbox("dash_rescan_btn", b2_x1, btn_y1, b2_x2, btn_y2, "Scan system for USB/Bluetooth gamepads")

    # 3. Minimize to Tray Button
    b3_x1 = b2_x2 + btn_gap
    b3_x2 = b3_x1 + btn_w
    draw_rounded_rect(canvas, b3_x1, btn_y1, b3_x2, btn_y2, radius=12, fill=T["card_hero_bg"], outline=T["card_border"], width=1)
    canvas.create_text((b3_x1 + b3_x2)//2, (btn_y1 + btn_y2)//2, text="🗕 Hide to System Tray", fill=T["text_muted"], font=("Segoe UI", 12, "bold"))
    register_hitbox("dash_minimize_tray_btn", b3_x1, btn_y1, b3_x2, btn_y2, "Hide window to system tray")
