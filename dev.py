"""
Live Development Hot-Reload Runner for BP Launcher
Monitors all python files in hydra_controller/ and instantly reloads the app upon saving.
"""
import os
import sys
import time
import subprocess

WATCH_DIRS = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "hydra_controller"),
    os.path.dirname(os.path.abspath(__file__))
]

def get_mtimes():
    """Returns a dict of {filepath: last_modified_timestamp} for all .py files."""
    mtimes = {}
    for watch_dir in WATCH_DIRS:
        for root, _, files in os.walk(watch_dir):
            if "venv" in root or "__pycache__" in root or ".git" in root or "build" in root or "dist" in root:
                continue
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    try:
                        mtimes[full_path] = os.path.getmtime(full_path)
                    except OSError:
                        pass
    return mtimes

def main():
    print("\n" + "="*60)
    print(" 🚀 BP Launcher Live Development Hot-Reloader Active")
    print(" Edit any file in VS Code and save (Ctrl+S) to see live changes!")
    print(" Press Ctrl+C in this terminal to stop.")
    print("="*60 + "\n")

    py_exe = sys.executable
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hydra_controller_daemon.py")

    current_process = subprocess.Popen([py_exe, script_path])
    last_mtimes = get_mtimes()

    try:
        while True:
            time.sleep(0.3)
            current_mtimes = get_mtimes()
            
            # Check if any file was modified, added, or deleted
            changed = False
            for path, mtime in current_mtimes.items():
                if path not in last_mtimes or mtime != last_mtimes[path]:
                    print(f"\n[⚡ Hot-Reload] File changed: {os.path.basename(path)} -> Restarting app...")
                    changed = True
                    break

            if not changed and len(current_mtimes) != len(last_mtimes):
                changed = True

            if changed:
                last_mtimes = current_mtimes
                # Terminate running process cleanly on Windows
                try:
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(current_process.pid)], capture_output=True)
                except Exception:
                    pass
                
                # Restart app with updated code
                time.sleep(0.15)
                current_process = subprocess.Popen([py_exe, script_path], cwd=os.path.dirname(os.path.abspath(__file__)))

            # If user manually closed the window, wait or restart on next save
            if current_process.poll() is not None and not changed:
                time.sleep(0.3)

    except KeyboardInterrupt:
        print("\nStopping Live Hot-Reloader...")
        try:
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(current_process.pid)], capture_output=True)
        except Exception:
            pass

if __name__ == "__main__":
    main()
