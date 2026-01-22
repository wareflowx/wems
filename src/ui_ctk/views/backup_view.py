"""
Backup View Module

Provides UI for:
- Manual backup creation
- Backup restoration
- Data export (Excel, CSV)
- Backup list display
"""

import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
import logging

from src.utils.backup_manager import BackupManager
from src.export.data_exporter import DataExporter

logger = logging.getLogger(__name__)


class BackupView(ctk.CTkFrame):
    """Backup and export management view."""

    def __init__(self, master, **kwargs):
        """
        Initialize backup view.

        Args:
            master: Parent widget (typically MainWindow)
            **kwargs: Additional arguments for CTkFrame
        """
        super().__init__(master, **kwargs)

        # Initialize managers
        self.backup_manager = BackupManager(
            database_path=Path("employee_manager.db"),
            backup_dir=Path("backups"),
            max_backups=30
        )

        self.exporter = DataExporter()

        # Build UI
        self.create_ui()
        self.refresh_backup_list()

    def create_ui(self):
        """Create backup management UI."""
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Backup and Export Management",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)

        # Backup management section
        backup_section = self._create_section_frame("Backup Management")

        # Create backup button
        create_backup_btn = ctk.CTkButton(
            backup_section,
            text="Create Backup",
            command=self.create_backup,
            width=200,
            height=35
        )
        create_backup_btn.pack(side="left", padx=5, pady=10)

        # Restore backup button
        restore_backup_btn = ctk.CTkButton(
            backup_section,
            text="Restore Backup",
            command=self.restore_backup,
            width=200,
            height=35
        )
        restore_backup_btn.pack(side="left", padx=5, pady=10)

        # Export section
        export_section = self._create_section_frame("Data Export")

        # Export to Excel button
        export_excel_btn = ctk.CTkButton(
            export_section,
            text="Export to Excel",
            command=self.export_excel,
            width=200,
            height=35
        )
        export_excel_btn.pack(side="left", padx=5, pady=10)

        # Export to CSV button
        export_csv_btn = ctk.CTkButton(
            export_section,
            text="Export to CSV",
            command=self.export_csv,
            width=200,
            height=35
        )
        export_csv_btn.pack(side="left", padx=5, pady=10)

        # Backup list section
        list_section = self._create_section_frame("Available Backups")

        # Backup list display
        self.backup_listbox = ctk.CTkTextbox(
            list_section,
            height=400,
            font=ctk.CTkFont(family="Consolas", size=11)
        )
        self.backup_listbox.pack(pady=10, fill="both", expand=True, padx=10)

        # Refresh button
        refresh_btn = ctk.CTkButton(
            list_section,
            text="Refresh List",
            command=self.refresh_backup_list,
            width=150
        )
        refresh_btn.pack(pady=5)

    def _create_section_frame(self, title: str) -> ctk.CTkFrame:
        """
        Create a section frame with title.

        Args:
            title: Section title

        Returns:
            CTkFrame widget
        """
        frame = ctk.CTkFrame(self)
        frame.pack(pady=10, fill="x", padx=20)

        # Title label
        title_label = ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(10, 5))

        return frame

    def create_backup(self):
        """Create a new backup."""
        try:
            backup_path = self.backup_manager.create_backup(description="manual")

            messagebox.showinfo(
                "Success",
                f"Backup created successfully:\n{backup_path.name}\n\n"
                f"Size: {backup_path.stat().st_size / (1024*1024):.2f} MB"
            )

            self.refresh_backup_list()
            logger.info(f"Manual backup created: {backup_path}")

        except FileNotFoundError as e:
            messagebox.showerror(
                "Error",
                f"Database file not found:\n{e}"
            )
            logger.error(f"Backup failed - database not found: {e}")

        except IOError as e:
            messagebox.showerror(
                "Error",
                f"Failed to create backup:\n{e}"
            )
            logger.error(f"Backup failed: {e}")

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Unexpected error creating backup:\n{e}"
            )
            logger.error(f"Unexpected error during backup: {e}")

    def refresh_backup_list(self):
        """Refresh the backup list display."""
        try:
            backups = self.backup_manager.list_backups()

            if not backups:
                text = "No backups available.\nClick 'Create Backup' to create your first backup."
            else:
                text = f"Total backups: {len(backups)}\n"
                text += f"Total size: {self.backup_manager.get_backup_size()} MB\n\n"

                for i, backup in enumerate(backups, 1):
                    text += f"[{i}] {backup['name']}\n"
                    text += f"    Size: {backup['size_mb']} MB\n"
                    text += f"    Created: {backup['created'].strftime('%Y-%m-%d %H:%M:%S')}\n\n"

            self.backup_listbox.delete("1.0", "end")
            self.backup_listbox.insert("1.0", text)

        except Exception as e:
            self.backup_listbox.delete("1.0", "end")
            self.backup_listbox.insert("1.0", f"Error loading backups: {e}")
            logger.error(f"Failed to load backup list: {e}")

    def restore_backup(self):
        """Restore selected backup."""
        try:
            # Show file dialog to select backup
            backup_path = filedialog.askopenfilename(
                title="Select Backup to Restore",
                initialdir=str(self.backup_manager.backup_dir),
                filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
            )

            if not backup_path:
                return

            # Confirm restoration
            confirm = messagebox.askyesno(
                "Confirm Restore",
                "Are you sure you want to restore this backup?\n\n"
                "The current database will be replaced.\n"
                "A pre-restore backup will be created automatically.\n\n"
                "Continue?"
            )

            if not confirm:
                return

            # Perform restore
            self.backup_manager.restore_backup(Path(backup_path))

            messagebox.showinfo(
                "Success",
                "Database restored successfully!\n\n"
                "The application will now close. Please restart to load the restored database."
            )

            logger.info(f"Backup restored from: {backup_path}")

            # Close application (user will need to restart)
            self.winfo_toplevel().destroy()

        except FileNotFoundError as e:
            messagebox.showerror(
                "Error",
                f"Backup file not found:\n{e}"
            )
            logger.error(f"Restore failed - file not found: {e}")

        except ValueError as e:
            messagebox.showerror(
                "Error",
                f"Invalid backup file:\n{e}"
            )
            logger.error(f"Restore failed - invalid file: {e}")

        except IOError as e:
            messagebox.showerror(
                "Error",
                f"Failed to restore backup:\n{e}"
            )
            logger.error(f"Restore failed: {e}")

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Unexpected error restoring backup:\n{e}"
            )
            logger.error(f"Unexpected error during restore: {e}")

    def export_excel(self):
        """Export all data to Excel."""
        try:
            save_path = filedialog.asksaveasfilename(
                title="Export to Excel",
                defaultextension=".xlsx",
                filetypes=[
                    ("Excel Files", "*.xlsx"),
                    ("All Files", "*.*")
                ],
                initialfile=f"employee_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )

            if not save_path:
                return

            self.exporter.export_all_to_excel(Path(save_path))

            messagebox.showinfo(
                "Success",
                f"Data exported successfully to:\n{save_path}"
            )

            logger.info(f"Excel export completed: {save_path}")

        except IOError as e:
            messagebox.showerror(
                "Error",
                f"Failed to export to Excel:\n{e}"
            )
            logger.error(f"Excel export failed: {e}")

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Unexpected error exporting to Excel:\n{e}"
            )
            logger.error(f"Unexpected error during Excel export: {e}")

    def export_csv(self):
        """Export to CSV."""
        try:
            save_path = filedialog.asksaveasfilename(
                title="Export to CSV",
                defaultextension=".csv",
                filetypes=[
                    ("CSV Files", "*.csv"),
                    ("All Files", "*.*")
                ],
                initialfile=f"employee_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )

            if not save_path:
                return

            self.exporter.export_to_csv(Path(save_path))

            messagebox.showinfo(
                "Success",
                f"Data exported successfully to:\n{save_path}"
            )

            logger.info(f"CSV export completed: {save_path}")

        except IOError as e:
            messagebox.showerror(
                "Error",
                f"Failed to export to CSV:\n{e}"
            )
            logger.error(f"CSV export failed: {e}")

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Unexpected error exporting to CSV:\n{e}"
            )
            logger.error(f"Unexpected error during CSV export: {e}")


# Import at end for datetime usage in export methods
from datetime import datetime
