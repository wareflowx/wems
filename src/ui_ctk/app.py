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
from employee.models import Caces, Employee, MedicalVisit, OnlineTraining
from ui_ctk.constants import (
    APP_NAME,
    APP_TITLE,
    APP_VERSION,
    DEFAULT_HEIGHT,
    DEFAULT_MODE,
    DEFAULT_THEME,
    DEFAULT_WIDTH,
)
from ui_ctk.main_window import MainWindow

# Import backup manager for automatic backups
from utils.backup_manager import BackupManager

# Import logging system
from utils.logging_config import setup_logging, get_logger

# Initialize logger
logger = get_logger(__name__)


def setup_customtkinter():
    """Configure CustomTkinter appearance and themes."""
    # Set appearance mode (System, Dark, Light)
    ctk.set_appearance_mode(DEFAULT_MODE)

    # Set color theme (blue, green, dark-blue)
    ctk.set_default_color_theme(DEFAULT_THEME)

    print("[OK] CustomTkinter configured")
    print(f"      Theme: {DEFAULT_MODE} mode, {DEFAULT_THEME} theme")


def setup_database(db_path: str = None):
    """
    Initialize database connection and create tables.

    Args:
        db_path: Path to SQLite database file (None = use config/env vars)
    """
    from utils.config import get_database_path, ensure_database_directory

    # Get database path from config if not specified
    if db_path is None:
        ensure_database_directory()
        db_file = get_database_path()
        print(f"[INFO] Using database from config/env: {db_file}")
    else:
        db_file = Path(db_path)

    # Check if database exists
    if not db_file.exists():
        print(f"[WARN] Database not found: {db_file}")
        print(f"[INFO] Creating new database: {db_file}")

    try:
        # Initialize database
        init_database(db_file)

        # Connect to database (if not already connected)
        if database.is_closed():
            database.connect()

        # Create tables if they don't exist
        database.create_tables(
            [
                Employee,
                Caces,
                MedicalVisit,
                OnlineTraining,
            ],
            safe=True,
        )

        print(f"[OK] Database initialized: {db_path}")
        print("      Connected successfully")

    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
        raise


def create_startup_backup(db_path: str = None):
    """
    Create automatic backup on application startup.

    Args:
        db_path: Path to database file (None = use config/env vars)
    """
    from utils.config import get_database_path

    # Get database path from config if not specified
    if db_path is None:
        db_file = get_database_path()
    else:
        db_file = Path(db_path)

    # Only create backup if database exists
    if not db_file.exists():
        print("[INFO] No existing database to backup")
        return

    try:
        backup_manager = BackupManager(
            database_path=db_file,
            backup_dir=Path("backups"),
            max_backups=30
        )

        backup_path = backup_manager.create_backup(description="startup")
        print(f"[OK] Startup backup created: {backup_path.name}")
        print(f"     Size: {backup_path.stat().st_size / (1024*1024):.2f} MB")

    except Exception as e:
        # Don't fail application if backup fails
        print(f"[WARN] Startup backup failed: {e}")
        print("[INFO] Application continuing without backup")


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

    print("[OK] Main window created")
    print(f"      Size: {DEFAULT_WIDTH}x{DEFAULT_HEIGHT}")

    return window


def show_main_application(app: ctk.CTk):
    """
    Show main application.

    Args:
        app: CustomTkinter root application
    """
    print("\n" + "=" * 50)
    print(" APPLICATION STARTING")
    print("=" * 50)
    print("\n[INFO] Press Ctrl+C or close window to exit\n")

    # Create main window and store reference for closing checks
    main_window = create_main_window(app)

    # Store reference globally for access in on_closing
    app.main_window = main_window


def main():
    """Application entry point."""
    print("=" * 50)
    print(f" {APP_NAME} v{APP_VERSION}")
    print(" Employee Management System")
    print("=" * 50)

    # Step 0: Setup logging
    setup_logging(level="INFO", enable_console=True, enable_file=True)
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")

    # Step 1: Setup CustomTkinter
    setup_customtkinter()

    # Step 2: Setup database
    setup_database()

    # Step 2.5: Create startup backup
    create_startup_backup()

    # Step 3: Create root application
    app = ctk.CTk()
    app.title(APP_TITLE)
    app.geometry(f"{DEFAULT_WIDTH}x{DEFAULT_HEIGHT}")

    # Set minimum window size
    app.minsize(DEFAULT_WIDTH, DEFAULT_HEIGHT)

    print("[OK] Application window created")

    # Step 4: Show main application
    show_main_application(app)

    # Step 5: Configure protocol for graceful shutdown
    def on_closing():
        """Handle application closing with unsaved changes check."""
        # Check for unsaved changes in main window
        if hasattr(app, 'main_window'):
            if app.main_window._check_current_view_unsaved():
                response = app.main_window._prompt_unsaved_changes()

                if response == 'cancel':
                    return  # Cancel closing
                elif response == 'save':
                    if not app.main_window._save_current_view():
                        return  # Save failed, cancel closing

        print("\n[INFO] Shutting down application...")
        logger.info("Application shutdown requested")

        # Close database connection
        if not database.is_closed():
            database.close()
            print("[OK] Database connection closed")
            logger.info("Database connection closed")

        # Log application shutdown
        logger.info(f"{APP_NAME} v{APP_VERSION} shutting down")

        # Quit application (will call destroy automatically)
        app.quit()

    app.protocol("WM_DELETE_WINDOW", on_closing)

    # Step 5: Start application loop
    try:
        app.mainloop()
    except KeyboardInterrupt:
        print("\n[INFO] Application interrupted by user")
        on_closing()

    print("[OK] Application closed cleanly")


if __name__ == "__main__":
    main()
