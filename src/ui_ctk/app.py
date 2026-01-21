#!/usr/bin/env python
"""
Wareflow EMS - CustomTkinter UI Main Entry Point

Desktop application for managing warehouse employees with their
safety certifications (CACES) and medical compliance tracking.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import customtkinter as ctk
from database.connection import database, init_database
from employee.models import Employee, Caces, MedicalVisit, OnlineTraining
from ui_ctk.main_window import MainWindow
from ui_ctk.constants import (
    APP_NAME,
    APP_TITLE,
    APP_VERSION,
    DEFAULT_WIDTH,
    DEFAULT_HEIGHT,
    DEFAULT_THEME,
    DEFAULT_MODE,
)


def setup_customtkinter():
    """Configure CustomTkinter appearance and themes."""
    # Set appearance mode (System, Dark, Light)
    ctk.set_appearance_mode(DEFAULT_MODE)

    # Set color theme (blue, green, dark-blue)
    ctk.set_default_color_theme(DEFAULT_THEME)

    print(f"[OK] CustomTkinter configured")
    print(f"      Theme: {DEFAULT_MODE} mode, {DEFAULT_THEME} theme")


def setup_database(db_path: str = "employee_manager.db"):
    """
    Initialize database connection and create tables.

    Args:
        db_path: Path to SQLite database file
    """
    # Check if database exists
    db_file = Path(db_path)

    if not db_file.exists():
        print(f"[WARN] Database not found: {db_path}")
        print(f"[INFO] Creating new database: {db_path}")

    try:
        # Initialize database
        init_database(db_file)

        # Connect to database (if not already connected)
        if database.is_closed():
            database.connect()

        # Create tables if they don't exist
        database.create_tables([
            Employee,
            Caces,
            MedicalVisit,
            OnlineTraining,
        ], safe=True)

        print(f"[OK] Database initialized: {db_path}")
        print(f"      Connected successfully")

    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
        raise


def create_main_window(app: ctk.CTk) -> MainWindow:
    """
    Create and configure main application window.

    Args:
        app: CustomTkinter root application

    Returns:
        Configured MainWindow instance
    """
    # Create main window
    window = MainWindow(app)
    window.pack(fill="both", expand=True)

    print(f"[OK] Main window created")
    print(f"      Size: {DEFAULT_WIDTH}x{DEFAULT_HEIGHT}")

    return window


def main():
    """Application entry point."""
    print("=" * 50)
    print(f" {APP_NAME} v{APP_VERSION}")
    print(" Employee Management System")
    print("=" * 50)

    # Step 1: Setup CustomTkinter
    setup_customtkinter()

    # Step 2: Setup database
    setup_database()

    # Step 3: Create root application
    app = ctk.CTk()
    app.title(APP_TITLE)
    app.geometry(f"{DEFAULT_WIDTH}x{DEFAULT_HEIGHT}")

    # Set minimum window size
    app.minsize(DEFAULT_WIDTH, DEFAULT_HEIGHT)

    print(f"[OK] Application window created")

    # Step 4: Create main window with navigation
    main_window = create_main_window(app)

    # Step 5: Configure protocol for graceful shutdown
    def on_closing():
        """Handle application closing."""
        print("\n[INFO] Shutting down application...")

        # Close database connection
        if not database.is_closed():
            database.close()
            print("[OK] Database connection closed")

        # Quit application (will call destroy automatically)
        app.quit()

    app.protocol("WM_DELETE_WINDOW", on_closing)

    # Step 6: Start application loop
    print("\n" + "=" * 50)
    print(" APPLICATION STARTING")
    print("=" * 50)
    print("\n[INFO] Press Ctrl+C or close window to exit\n")

    try:
        app.mainloop()
    except KeyboardInterrupt:
        print("\n[INFO] Application interrupted by user")
        on_closing()

    print("[OK] Application closed cleanly")


if __name__ == "__main__":
    main()
