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

# Import authentication system
from auth.models import User, create_tables
from auth.session import get_current_user, is_authenticated
from ui_ctk.views.login_view import LoginView, create_default_admin

# Import logging system
from utils.logging_config import setup_logging, get_logger
from utils.security_logger import log_authentication, log_authorization

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

        # Create authentication tables
        create_tables()

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


def create_main_window(app: ctk.CTk, user: User) -> MainWindow:
    """
    Create and configure main application window.

    Args:
        app: CustomTkinter root application
        user: Authenticated user

    Returns:
        Configured MainWindow instance
    """
    # Create main window
    window = MainWindow(app)
    window.pack(fill="both", expand=True)

    # Pass user to window for future use (permissions, etc.)
    window.current_user = user

    print("[OK] Main window created")
    print(f"      User: {user.username} ({user.role})")
    print(f"      Size: {DEFAULT_WIDTH}x{DEFAULT_HEIGHT}")

    return window


def show_login_screen(app: ctk.CTk):
    """
    Show login screen and handle authentication.

    Args:
        app: CustomTkinter root application
    """
    print("\n" + "=" * 50)
    print(" AUTHENTICATION REQUIRED")
    print("=" * 50)

    # Log authentication requirement
    logger.info("Authentication required, showing login screen")

    # Ensure default admin exists
    admin = create_default_admin()
    if admin:
        print(f"\n[INFO] Default admin account created:")
        print(f"       Username: {admin.username}")
        print(f"       Password: Admin123!")
        print(f"       Email: {admin.email}")
        print(f"\n[WARN] Please change the default password after first login!\n")
        logger.warning(f"Default admin account created: {admin.username}")

    # Create and show login view
    login_view = LoginView(app, login_success_callback=lambda user: on_login_success(app, user))
    login_view.pack(fill="both", expand=True)

    print("[OK] Login screen displayed")


def on_login_success(app: ctk.CTk, user: User):
    """
    Handle successful user login.

    Args:
        app: CustomTkinter root application
        user: Authenticated user
    """
    # Log successful authentication
    log_authentication(
        "login",
        user.username,
        success=True,
    )
    logger.info(f"User logged in: {user.username} (role: {user.role})")

    # Show main application
    show_main_application(app, user)


def show_main_application(app: ctk.CTk, user: User):
    """
    Show main application after successful login.

    Args:
        app: CustomTkinter root application
        user: Authenticated user
    """
    print("\n" + "=" * 50)
    print(" ACCESS GRANTED")
    print("=" * 50)
    print(f"User: {user.username}")
    print(f"Role: {user.role}")
    print("=" * 50 + "\n")

    # Clear login view
    for widget in app.winfo_children():
        widget.destroy()

    # Create main window
    main_window = create_main_window(app, user)

    print("\n" + "=" * 50)
    print(" APPLICATION STARTING")
    print("=" * 50)
    print("\n[INFO] Press Ctrl+C or close window to exit\n")


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

    # Step 4: Show login screen (authentication required)
    show_login_screen(app)

    # Step 5: Configure protocol for graceful shutdown
    def on_closing():
        """Handle application closing."""
        print("\n[INFO] Shutting down application...")
        logger.info("Application shutdown requested")

        # Log logout if authenticated
        if is_authenticated():
            user = get_current_user()
            print(f"[INFO] Logging out: {user.username}")
            log_authentication("logout", user.username, success=True)
            logger.info(f"User logged out: {user.username}")

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

    # Step 6: Start application loop
    try:
        app.mainloop()
    except KeyboardInterrupt:
        print("\n[INFO] Application interrupted by user")
        on_closing()

    print("[OK] Application closed cleanly")


if __name__ == "__main__":
    main()
