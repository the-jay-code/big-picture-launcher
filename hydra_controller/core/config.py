import os
import json
from typing import Dict, Any

CREATE_NO_WINDOW = 0x08000000
REG_RUN_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_REG_NAME = "BPLauncher"

DEFAULT_CONNECT_DEBOUNCE = 0.3
DEFAULT_DISCONNECT_DEBOUNCE = 1.0
DEFAULT_POLL_INTERVAL = 0.20
DEFAULT_EXCLUDED_KEYWORDS = [
    "mouse", "keyboard", "macro", "virtual", "headset", "audio", "vjoy", "passthrough"
]

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "hydra_bento_config.json")

DEFAULT_CONFIG: Dict[str, Any] = {
    "theme_mode": "dark",
    "target_launcher": "hydra",
    "auto_launch_on_controller": True,
    "kill_on_disconnect": False,
    "big_picture_mode": False,
    "minimize_to_tray": True,
    "sound_alerts": True,
    "toast_notifications": True,
    "guide_shortcut_enabled": True,
    "poll_interval": DEFAULT_POLL_INTERVAL,
    "connect_debounce": DEFAULT_CONNECT_DEBOUNCE,
    "disconnect_debounce": DEFAULT_DISCONNECT_DEBOUNCE,
    "launcher_paths": {
        "hydra": "",
        "steam": "",
        "playnite": "",
        "custom": ""
    },
    "custom_hydra_path": "",
    "excluded_keywords": DEFAULT_EXCLUDED_KEYWORDS
}

THEMES = {
    "dark": {
        "window_bg": "#0a0f19",
        "outer_border": "#1a273e",
        "canvas_bg": "#0d1424",
        "rail_bg": "#111b2e",
        "card_hero_bg": "#142036",
        "card_hero_border": "#213454",
        "card_bg": "#121d30",
        "card_border": "#1c2c47",
        "card_inner_bg": "#0c1527",
        "pill_dark": "#182740",
        "pill_light": "#e0f2fe",
        "pill_accent": "#38bdf8",
        "text_light": "#f8fafc",
        "text_sub": "#cbd5e1",
        "text_muted": "#889db8",
        "text_dark": "#0c1527",
        "active_blue": "#38bdf8",
        "active_blue_bg": "#0c3258",
        "active_green": "#22c55e",
        "active_green_bg": "#14532d",
        "danger_red": "#ef4444",
        "accent_cyan": "#38bdf8",
        "accent_soft_blue": "#7dd3fc",
        "accent_purple": "#818cf8",
        "accent_gold": "#f59e0b"
    },
    "light": {
        "window_bg": "#e0f2fe",
        "outer_border": "#bae6fd",
        "canvas_bg": "#f0f9ff",
        "rail_bg": "#ffffff",
        "card_hero_bg": "#ffffff",
        "card_hero_border": "#bae6fd",
        "card_bg": "#ffffff",
        "card_border": "#e0f2fe",
        "card_inner_bg": "#f0f9ff",
        "pill_dark": "#e0f2fe",
        "pill_light": "#0284c7",
        "pill_accent": "#0ea5e9",
        "text_light": "#0f172a",
        "text_sub": "#334155",
        "text_muted": "#64748b",
        "text_dark": "#ffffff",
        "active_blue": "#0284c7",
        "active_blue_bg": "#e0f2fe",
        "active_green": "#16a34a",
        "active_green_bg": "#dcfce7",
        "danger_red": "#dc2626",
        "accent_cyan": "#0284c7",
        "accent_soft_blue": "#0ea5e9",
        "accent_purple": "#6366f1",
        "accent_gold": "#d97706"
    }
}


def load_config() -> Dict[str, Any]:
    cfg = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                cfg.update(loaded)
                if "launcher_paths" not in cfg:
                    cfg["launcher_paths"] = DEFAULT_CONFIG["launcher_paths"].copy()
        except Exception as e:
            print(f"Error loading config: {e}")
    return cfg


def save_config(cfg: Dict[str, Any]):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception as e:
        print(f"Error saving config: {e}")
