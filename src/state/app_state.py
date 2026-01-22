"""Global application state management."""

import sys
from pathlib import Path
from typing import Optional

# Add src directory to path for imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from lock.manager import LockManager, get_process_info


class AppState:
    """
    Centralized global state for the application.

    Manages:
    - Lock manager instance for database access control
    - Currently selected employee ID for detail view navigation
    - Theme mode (light/dark)
    - Alert thresholds for compliance warnings

    This state is shared across all views and components.
    """

    def __init__(self):
        """Initialize the application state with default values."""
        # Lock manager for database access control
        hostname, username, pid = get_process_info()
        self.lock_manager: LockManager = LockManager(hostname=hostname, username=username, pid=pid)

        # Currently selected employee (for detail view navigation)
        self.current_employee_id: Optional[int] = None

        # Theme mode: True = light, False = dark
        self.theme_mode: bool = True

        # Alert thresholds (in days before expiration)
        self.caces_alert_threshold: int = 90
        self.medical_alert_threshold: int = 90
        self.training_alert_threshold: int = 90

        # Lock status tracking
        self._lock_status: str = "Unlocked"
        self._lock_lost_callback = None

    def acquire_lock(self) -> bool:
        """
        Acquire the application lock.

        Returns:
            True if lock was acquired successfully, False otherwise
        """
        try:
            self.lock_manager.acquire_lock()
            self._lock_status = f"Locked by {self.lock_manager.hostname}"
            return True
        except RuntimeError as e:
            self._lock_status = f"Lock failed: {str(e)}"
            return False
        except Exception as e:
            self._lock_status = f"Lock error: {str(e)}"
            return False

    def release_lock(self) -> bool:
        """
        Release the application lock.

        Returns:
            True if lock was released successfully, False otherwise
        """
        try:
            success = self.lock_manager.release_lock()
            if success:
                self._lock_status = "Unlocked"
            return success
        except Exception:
            return False

    def check_lock_health(self) -> bool:
        """
        Check if the lock is still held by this process.

        Returns:
            True if lock is still active, False otherwise
        """
        return self.lock_manager.check_lock_health()

    @property
    def lock_status(self) -> str:
        """Get current lock status display text."""
        return self._lock_status

    def set_lock_lost_callback(self, callback):
        """
        Set a callback function to be called if lock is lost.

        Args:
            callback: Function to call when lock is lost
        """
        self._lock_lost_callback = callback

    def get_hostname(self) -> str:
        """Get the current hostname."""
        return self.lock_manager.hostname

    def get_username(self) -> Optional[str]:
        """Get the current username."""
        return self.lock_manager.username

    def set_employee(self, employee_id: int):
        """
        Set the currently selected employee ID.

        Args:
            employee_id: ID of the employee to view
        """
        self.current_employee_id = employee_id

    def get_employee(self) -> Optional[int]:
        """
        Get the currently selected employee ID.

        Returns:
            Employee ID or None if no employee is selected
        """
        return self.current_employee_id

    def clear_employee(self):
        """Clear the currently selected employee."""
        self.current_employee_id = None

    def toggle_theme(self):
        """Toggle between light and dark theme."""
        self.theme_mode = not self.theme_mode

    def set_theme(self, is_light: bool):
        """
        Set the theme mode.

        Args:
            is_light: True for light theme, False for dark theme
        """
        self.theme_mode = is_light

    def is_light_theme(self) -> bool:
        """
        Check if current theme is light mode.

        Returns:
            True if light theme, False for dark theme
        """
        return self.theme_mode


# Global singleton instance
_app_state_instance: Optional[AppState] = None


def get_app_state() -> AppState:
    """
    Get the global application state instance.

    Returns:
        The singleton AppState instance
    """
    global _app_state_instance
    if _app_state_instance is None:
        _app_state_instance = AppState()
    return _app_state_instance


def reset_app_state():
    """Reset the global application state (mainly for testing)."""
    global _app_state_instance
    _app_state_instance = None
