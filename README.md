# 🎮 BP Launcher (Big Picture Edition)

> **A high-performance, zero-resource background gamepad automation daemon and hardware monitor for Windows.**

Automate launching **Hydra Launcher**, **Steam Big Picture**, **Playnite Fullscreen**, or any custom game/executable the moment you connect your Xbox, PlayStation, or Switch controller.

---

## ⚡ Key Features

- **0.0% Idle CPU Utilization**: Built with an optimized event loop that consumes virtually zero system resources in the background.
- **24/7 Background Tray Service**: Minimizes silently to the Windows notification tray with instant controller connection triggers.
- **Dedicated Telemetry & Calibration Lab**: Real-time dual analog thumbstick radar crosshairs, radial deadzone drift filtering, trigger pressure gauges (`LT` & `RT`), and live physical button matrix (`Ⓐ Ⓑ Ⓧ Ⓨ`, bumpers, triggers, D-Pad, sticks).
- **Haptic Vibration Test**: Integrated rumble motor test pulse (`joy.rumble()`).
- **Controller Hotplug Automation**: Automatically detects Xbox (XInput), PlayStation (DualSense/DualShock), and Nintendo Switch controllers.
- **Multi-Launcher Presets**: Quick switching and custom executable path pickers for:
  - 🐉 **Hydra Launcher**
  - 💨 **Steam Big Picture**
  - 🎮 **Playnite Fullscreen**
  - 🕹 **Custom Games & Executables**
- **Windows Startup Integration**: Optional silent boot registration via Windows Registry (`HKCU\Software\Microsoft\Windows\CurrentVersion\Run`).
- **Guide / Home Long-Press Shortcut**: Hold the Guide button (or `L3 + R3`) for 1.2s to focus or toggle your game launcher.
- **In-App Dynamic Hot-Reloading**: Real-time module hot-reloading on file save without restarting the application.
- **Modern Bento UI**: Sleek vector-rendered design with dark and light theme options.

---

## 🚀 Quick Start

### 1. Requirements
- Windows 10 / 11
- Python 3.10+

### 2. Installation
```powershell
# Clone the repository
git clone https://github.com/the-jay-code/big-picture-launcher.git
cd big-picture-launcher

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run
```powershell
python hydra_controller_daemon.py
```

---

## 📦 Standalone Portable Executable (.exe) Build

To compile a single-file portable Windows executable that runs without Python:

```powershell
pip install pyinstaller
pyinstaller --noconsole --onefile --name "BPLauncher" hydra_controller_daemon.py
```
The compiled executable will be located in the `dist/` directory.

---

## 🛠 Project Architecture

```
bp-launcher/
├── hydra_controller/
│   ├── main.py                     # Application entrypoint
│   ├── core/
│   │   ├── config.py               # Theme palettes, defaults & JSON persistence
│   │   ├── system.py               # Windows Registry startup, process launcher & paths
│   │   ├── daemon.py               # Pygame joystick monitor, telemetry, rumble haptics
│   │   └── tray.py                 # Pystray notification service & dynamic tray icon
│   └── ui/
│       ├── geometry.py             # Anti-aliased rounded polygon geometry engine
│       ├── app.py                  # Main CTk window, navigation router & hitbox dispatcher
│       └── pages/
│           ├── dashboard.py        # Hero gamepad card, telemetry radar HUD, quick actions
│           ├── settings.py         # Dynamic scaling settings, custom path pickers
│           └── about.py            # Developer card, GitHub links, system diagnostics
├── hydra_controller_daemon.py      # Bootstrap runner
└── requirements.txt
```

---

## 👤 Credits & License

- **Developer**: [@the-jay-code](https://github.com/the-jay-code)
- **Official Hydra Project**: [hydralauncher/hydra](https://github.com/hydralauncher/hydra)
- **License**: MIT License
