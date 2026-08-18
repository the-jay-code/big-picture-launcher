"""
Hydra Controller Monitor Daemon
Bootstrap runner for hydra_controller package.
"""
import os
import sys

# Add workspace directory to path
workspace_dir = os.path.dirname(os.path.abspath(__file__))
if workspace_dir not in sys.path:
    sys.path.insert(0, workspace_dir)

from hydra_controller.main import main

if __name__ == "__main__":
    main()