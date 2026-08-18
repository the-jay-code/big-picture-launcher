"""
Hydra Controller Monitor Main Application Entry Point
"""
import os
import sys

# Ensure quiet pygame initialization
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

from hydra_controller.ui.app import BentoHydraApp


def main():
    app = BentoHydraApp()
    app.mainloop()


if __name__ == "__main__":
    main()
