import os
import sys
import shutil
import subprocess
import winreg
import logging
from typing import Dict, Any

from hydra_controller.core.config import CREATE_NO_WINDOW, REG_RUN_PATH, APP_REG_NAME

logger = logging.getLogger("hydra_bento")


def is_windows_startup_enabled() -> bool:
    """Checks if the application is registered to run on Windows startup."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_PATH, 0, winreg.KEY_READ)
        val, _ = winreg.QueryValueEx(key, APP_REG_NAME)
        winreg.CloseKey(key)
        return bool(val)
    except Exception:
        return False


def set_windows_startup_enabled(enabled: bool):
    """Registers or unregisters the app from Windows startup registry."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_PATH, 0, winreg.KEY_SET_VALUE)
        if enabled:
            py_exe = sys.executable
            main_script = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "hydra_controller_daemon.py"))
            pyw_exe = py_exe.replace("python.exe", "pythonw.exe")
            if not os.path.exists(pyw_exe):
                pyw_exe = py_exe
            cmd = f'"{pyw_exe}" "{main_script}"'
            winreg.SetValueEx(key, APP_REG_NAME, 0, winreg.REG_SZ, cmd)
        else:
            try:
                winreg.DeleteValue(key, APP_REG_NAME)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
    except Exception as e:
        logger.error(f"Registry startup error: {e}")


def is_process_running(process_name: str) -> bool:
    try:
        result = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq {process_name}"],
            capture_output=True,
            creationflags=CREATE_NO_WINDOW,
            text=True
        )
        return process_name in result.stdout
    except Exception:
        return False


def find_hydra_exe(cfg: Dict[str, Any]) -> str:
    custom = cfg.get("launcher_paths", {}).get("hydra", "") or cfg.get("custom_hydra_path", "")
    if custom and os.path.exists(custom):
        return custom

    local_appdata = os.environ.get('LOCALAPPDATA', '')
    appdata = os.environ.get('APPDATA', '')
    program_files = os.environ.get('ProgramFiles', 'C:\\Program Files')
    program_files_x86 = os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')

    possible_paths = [
        os.path.join(local_appdata, 'Programs', 'hydra', 'Hydra.exe'),
        os.path.join(local_appdata, 'hydra', 'Hydra.exe'),
        os.path.join(local_appdata, 'Programs', 'Hydra', 'Hydra.exe'),
        os.path.join(local_appdata, 'Programs', 'Hydra Launcher', 'Hydra.exe'),
        os.path.join(appdata, 'hydra', 'Hydra.exe'),
        os.path.join(program_files, 'Hydra', 'Hydra.exe'),
        os.path.join(program_files_x86, 'Hydra', 'Hydra.exe'),
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    which_result = shutil.which('Hydra.exe')
    if which_result:
        return which_result

    return 'Hydra.exe'


def find_steam_exe(cfg: Dict[str, Any]) -> str:
    custom = cfg.get("launcher_paths", {}).get("steam", "")
    if custom and os.path.exists(custom):
        return custom
    
    program_files_x86 = os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')
    program_files = os.environ.get('ProgramFiles', 'C:\\Program Files')
    
    for base in [program_files_x86, program_files, "C:\\Steam", "D:\\Steam"]:
        p = os.path.join(base, "Steam", "steam.exe")
        if os.path.exists(p):
            return p
    return "steam.exe"


def find_playnite_exe(cfg: Dict[str, Any]) -> str:
    custom = cfg.get("launcher_paths", {}).get("playnite", "")
    if custom and os.path.exists(custom):
        return custom

    local_appdata = os.environ.get('LOCALAPPDATA', '')
    p = os.path.join(local_appdata, 'Playnite', 'Playnite.FullscreenApp.exe')
    if os.path.exists(p):
        return p
    p2 = os.path.join(local_appdata, 'Playnite', 'Playnite.DesktopApp.exe')
    if os.path.exists(p2):
        return p2
    return "Playnite.FullscreenApp.exe"


def get_launcher_path(cfg: Dict[str, Any], key: str) -> str:
    custom = cfg.get("launcher_paths", {}).get(key, "")
    if custom and os.path.exists(custom):
        return custom
    
    if key == "hydra":
        return find_hydra_exe(cfg)
    elif key == "steam":
        return find_steam_exe(cfg)
    elif key == "playnite":
        return find_playnite_exe(cfg)
    elif key == "custom":
        return cfg.get("custom_hydra_path", "")
    return ""


def launch_target_launcher(cfg: Dict[str, Any]):
    target = cfg.get("target_launcher", "hydra")

    if target == "steam":
        logger.info("Opening Steam in Big Picture mode...")
        steam_p = get_launcher_path(cfg, "steam")
        if os.path.exists(steam_p):
            subprocess.Popen([steam_p, "-bigpicture"], creationflags=CREATE_NO_WINDOW)
        else:
            try:
                os.startfile("steam://open/bigpicture")
            except Exception as e:
                logger.error(f"Steam launch failed: {e}")
        return

    if target == "playnite":
        logger.info("Launching Playnite Fullscreen...")
        playnite_path = get_launcher_path(cfg, "playnite")
        if os.path.exists(playnite_path):
            subprocess.Popen([playnite_path], creationflags=CREATE_NO_WINDOW)
        return

    if target == "custom":
        custom_p = get_launcher_path(cfg, "custom")
        if custom_p and os.path.exists(custom_p):
            subprocess.Popen([custom_p], creationflags=CREATE_NO_WINDOW)
        return

    # Default Hydra
    if is_process_running("Hydra.exe"):
        logger.info("Hydra is already running.")
        return

    hydra_path = get_launcher_path(cfg, "hydra")
    flags = ["--big-picture"] if cfg.get("big_picture_mode", False) else []
    try:
        subprocess.Popen(
            [hydra_path] + flags,
            creationflags=CREATE_NO_WINDOW
        )
        logger.info(f"Launched Hydra Launcher ({hydra_path})")
    except Exception as e:
        logger.error(f"Launch failed ({hydra_path}): {e}")


def kill_target_launcher(cfg: Dict[str, Any]):
    try:
        subprocess.run(
            ["taskkill", "/F", "/IM", "Hydra.exe"],
            capture_output=True,
            creationflags=CREATE_NO_WINDOW
        )
    except Exception:
        pass
