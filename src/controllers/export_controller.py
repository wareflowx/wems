"""Export controller for UI operations.

This module provides the controller layer for Excel export functionality in the UI.
It handles background thread execution, progress tracking, and error handling.
"""

import threading
from pathlib import Path
from typing import Callable, Optional

from database.models import Employee
from export.excel import export_employees_to_excel


class ExportController:
    """Controller for managing Excel export operations from the UI."""

    def __init__(self):
        """Initialize the export controller."""
        self._export_thread: Optional[threading.Thread] = None
        self._is_exporting = False

    def export_employees(
        self,
        output_path: Path,
        employees: list[Employee],
        include_caces: bool = True,
        include_visits: bool = True,
        include_trainings: bool = True,
        progress_callback: Optional[Callable[[str, int], None]] = None,
        completion_callback: Optional[Callable[[bool, str], None]] = None,
    ) -> bool:
        """
        Export employees to Excel in a background thread.

        Args:
            output_path: Path where the Excel file will be saved
            employees: List of employees to export
            include_caces: Whether to include CACES sheet
            include_visits: Whether to include medical visits sheet
            include_trainings: Whether to include training sheet
            progress_callback: Optional callback function(progress_message, percentage)
            completion_callback: Optional callback function(success, message)

        Returns:
            True if export was started successfully, False if already exporting
        """
        if self._is_exporting:
            if completion_callback:
                completion_callback(False, "An export is already in progress")
            return False

        self._is_exporting = True

        def export_worker():
            """Worker function that runs in background thread."""
            try:
                if progress_callback:
                    progress_callback("Starting export...", 0)

                export_employees_to_excel(
                    output_path=output_path,
                    employees=employees,
                    include_caces=include_caces,
                    include_visits=include_visits,
                    include_trainings=include_trainings,
                )

                if progress_callback:
                    progress_callback("Export completed successfully", 100)

                if completion_callback:
                    completion_callback(True, f"Export saved to {output_path}")

            except PermissionError as e:
                error_msg = str(e)
                if progress_callback:
                    progress_callback("Permission error", 0)

                if completion_callback:
                    completion_callback(False, error_msg)

            except IOError as e:
                error_msg = f"Failed to write file: {e}"
                if progress_callback:
                    progress_callback("IO error", 0)

                if completion_callback:
                    completion_callback(False, error_msg)

            except Exception as e:
                error_msg = f"Unexpected error during export: {e}"
                if progress_callback:
                    progress_callback("Error", 0)

                if completion_callback:
                    completion_callback(False, error_msg)

            finally:
                self._is_exporting = False

        # Start background thread
        self._export_thread = threading.Thread(target=export_worker, daemon=True)
        self._export_thread.start()

        return True

    def is_exporting(self) -> bool:
        """
        Check if an export is currently in progress.

        Returns:
            True if exporting, False otherwise
        """
        return self._is_exporting

    def cancel_export(self) -> bool:
        """
        Cancel the current export operation.

        Note: This is a graceful cancellation request. The export thread
        will complete its current operation before stopping.

        Returns:
            True if export was in progress, False otherwise
        """
        if not self._is_exporting:
            return False

        # Note: We can't forcefully kill threads in Python
        # The export will complete naturally
        self._is_exporting = False
        return True
