"""Warehouse Employee Management System - Main Entry Point

This module serves as the main entry point for the application.
It imports and runs the CustomTkinter GUI application.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the GUI application
if __name__ == "__main__":
    from ui_ctk.app import main

    main()
