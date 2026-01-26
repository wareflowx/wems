"""Trash view for viewing and restoring deleted items."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import customtkinter as ctk

from employee.models import Caces, Employee, MedicalVisit, OnlineTraining
from ui_ctk.constants import BTN_BACK
from ui_ctk.views.base_view import BaseView


class TrashView(BaseView):
    """
    View for viewing and restoring soft-deleted items.

    Displays all soft-deleted employees, CACES, medical visits, and trainings
    with options to restore or permanently delete them.
    """

    def __init__(self, master):
        """Initialize trash view.

        Args:
            master: Parent widget
        """
        # Call parent WITHOUT title to avoid duplicate header
        super().__init__(master, title="")

        # Create UI
        self.create_header()
        self.create_content()

    def create_header(self):
        """Create view header with title and empty button."""
        header = ctk.CTkFrame(self, height=60)
        header.pack(side="top", fill="x", padx=10, pady=(10, 5))
        header.pack_propagate(False)

        # Title and empty trash button
        title_label = ctk.CTkLabel(header, text="🗑️ Trash - Deleted Items", font=("Arial", 18, "bold"))
        title_label.pack(side="left", padx=20)

        # Count label
        self.count_label = ctk.CTkLabel(header, text="Loading...", font=("Arial", 12))
        self.count_label.pack(side="left", padx=20)

        # Refresh button
        btn_refresh = ctk.CTkButton(header, text="Refresh", width=100, command=self.refresh_view)
        btn_refresh.pack(side="right", padx=5)

        # Empty trash button (red, dangerous)
        btn_empty = ctk.CTkButton(
            header,
            text="Empty Trash",
            width=120,
            command=self.confirm_empty_trash,
            fg_color="#c42b1f",
            hover_color="#a33d2e",
        )
        btn_empty.pack(side="right", padx=5)

    def create_content(self):
        """Create main content area with tabbed interface for deleted items."""
        # Create scrollable content area
        content_frame = ctk.CTkScrollableFrame(self, height=500)
        content_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        # Store reference for refreshing
        self.content_frame = content_frame

        # Load and display deleted items
        self.load_deleted_items()

    def load_deleted_items(self):
        """Load and display all deleted items grouped by type."""
        # Clear existing content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Get deleted employees
        deleted_employees = list(Employee.deleted().order_by(Employee.deleted_at.desc()))
        deleted_caces = list(Caces.deleted().order_by(Caces.deleted_at.desc()))
        deleted_visits = list(MedicalVisit.deleted().order_by(MedicalVisit.deleted_at.desc()))
        deleted_trainings = list(OnlineTraining.deleted().order_by(OnlineTraining.deleted_at.desc()))

        # Update count
        total_deleted = (
            len(deleted_employees)
            + len(deleted_caces)
            + len(deleted_visits)
            + len(deleted_trainings)
        )
        self.count_label.configure(text=f"{total_deleted} items")

        # Display by category
        self._display_section("Employees", deleted_employees, "employee")
        self._display_section("CACES", deleted_caces, "caces")
        self._display_section("Medical Visits", deleted_visits, "visit")
        self._display_section("Trainings", deleted_trainings, "training")

    def _display_section(self, title: str, items, item_type: str):
        """Display a section of deleted items.

        Args:
            title: Section title
            items: List of deleted items
            item_type: Type of items ('employee', 'caces', 'visit', 'training')
        """
        if not items:
            return

        # Section header
        section_header = ctk.CTkFrame(self.content_frame, height=40)
        section_header.pack(fill="x", pady=(10, 5))
        section_header.pack_propagate(False)

        title_label = ctk.CTkLabel(
            section_header, text=f"{title} ({len(items)})", font=("Arial", 14, "bold")
        )
        title_label.pack(side="left", padx=20, pady=10)

        # Display each item
        for item in items:
            item_frame = ctk.CTkFrame(self.content_frame)
            item_frame.pack(fill="x", padx=20, pady=2)

            self._create_item_row(item_frame, item, item_type)

    def _create_item_row(self, parent, item, item_type: str):
        """Create a row for a deleted item.

        Args:
            parent: Parent frame
            item: The deleted item
            item_type: Type of item
        """
        # Get display text based on item type
        if item_type == "employee":
            primary_text = f"👤 {item.full_name}"
            secondary_text = f"ID: {item.external_id or 'N/A'} | {item.role}"
            delete_info = f"Deleted: {self._format_datetime(item.deleted_at)}"
        elif item_type == "caces":
            primary_text = f"🏭️ CACES {item.kind}"
            secondary_text = f"Employee: {item.employee.full_name}"
            delete_info = f"Deleted: {self._format_datetime(item.deleted_at)}"
        elif item_type == "visit":
            primary_text = f"🏥 Medical Visit - {item.visit_type}"
            secondary_text = f"Employee: {item.employee.full_name}"
            delete_info = f"Deleted: {self._format_datetime(item.deleted_at)}"
        elif item_type == "training":
            primary_text = f"📚 Training: {item.title}"
            secondary_text = f"Employee: {item.employee.full_name}"
            delete_info = f"Deleted: {self._format_datetime(item.deleted_at)}"
        else:
            primary_text = "Unknown Item"
            secondary_text = ""
            delete_info = ""

        # Item info
        info_frame = ctk.CTkFrame(parent, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=8)

        # Primary text
        primary_label = ctk.CTkLabel(info_frame, text=primary_text, font=("Arial", 12, "bold"))
        primary_label.pack(anchor="w")

        # Secondary text
        if secondary_text:
            secondary_label = ctk.CTkLabel(info_frame, text=secondary_text, font=("Arial", 10))
            secondary_label.pack(anchor="w")

        # Delete info
        if delete_info:
            delete_label = ctk.CTkLabel(info_frame, text=delete_info, font=("Arial", 9), text_color="gray")
            delete_label.pack(anchor="w")

        # Action buttons
        btn_restore = ctk.CTkButton(
            parent,
            text="Restore",
            width=100,
            command=lambda i=item, t=item_type: self.restore_item(i, t),
        )
        btn_restore.pack(side="right", padx=5, pady=8)

        btn_delete = ctk.CTkButton(
            parent,
            text="Delete Permanently",
            width=120,
            command=lambda i=item, t=item_type: self.confirm_permanent_delete(i, t),
            fg_color="#c42b1f",
            hover_color="#a33d2e",
        )
        btn_delete.pack(side="right", padx=5, pady=8)

    def restore_item(self, item, item_type: str):
        """Restore a soft-deleted item.

        Args:
            item: The item to restore
            item_type: Type of item
        """
        try:
            # Restore the item
            item.restore()

            print(f"[OK] Restored {item_type}: {item}")

            # Refresh view
            self.refresh_view()

        except Exception as e:
            print(f"[ERROR] Failed to restore {item_type}: {e}")
            self.show_error(f"Failed to restore item: {e}")

    def confirm_permanent_delete(self, item, item_type: str):
        """Confirm and permanently delete an item.

        Args:
            item: The item to permanently delete
            item_type: Type of item
        """
        try:
            import tkinter.messagebox as messagebox

            # Get item description
            if item_type == "employee":
                description = f"{item.full_name} (ID: {item.external_id or 'N/A'})"
            elif item_type == "caces":
                description = f"CACES {item.kind} for {item.employee.full_name}"
            elif item_type == "visit":
                description = f"Medical visit for {item.employee.full_name}"
            elif item_type == "training":
                description = f"Training '{item.title}' for {item.employee.full_name}"
            else:
                description = "this item"

            # Show confirmation
            confirm = messagebox.askyesno(
                "Permanently Delete",
                f"Are you sure you want to PERMANENTLY delete:\n\n{description}\n\n"
                "This action CANNOT be undone!",
                icon="warning",
            )

            if confirm:
                # Permanently delete
                item.delete_instance()
                print(f"[OK] Permanently deleted {item_type}: {description}")

                # Refresh view
                self.refresh_view()

        except Exception as e:
            print(f"[ERROR] Failed to delete {item_type}: {e}")
            self.show_error(f"Failed to delete item: {e}")

    def confirm_empty_trash(self):
        """Confirm and empty all trash."""
        try:
            import tkinter.messagebox as messagebox

            # Get counts
            emp_count = Employee.deleted().count()
            caces_count = Caces.deleted().count()
            visits_count = MedicalVisit.deleted().count()
            training_count = OnlineTraining.deleted().count()

            total = emp_count + caces_count + visits_count + training_count

            if total == 0:
                messagebox.showinfo("Trash Empty", "The trash is already empty.")
                return

            # Show confirmation
            message = (
                f"Are you sure you want to permanently delete ALL items in trash?\n\n"
                f"Total items: {total}\n"
                f"- Employees: {emp_count}\n"
                f"- CACES: {caces_count}\n"
                f"- Medical Visits: {visits_count}\n"
                f"- Trainings: {training_count}\n\n"
                "This action CANNOT be undone!"
            )

            confirm = messagebox.askyesno("Empty Trash", message, icon="warning")

            if confirm:
                # Permanently delete all items
                Employee.deleted().delete_instance()
                Caces.deleted().delete_instance()
                MedicalVisit.deleted().delete_instance()
                OnlineTraining.deleted().delete_instance()

                print(f"[OK] Emptied trash: {total} items permanently deleted")

                # Refresh view
                self.refresh_view()

                # Show success message
                messagebox.showinfo("Trash Emptied", f"Successfully deleted {total} items.")

        except Exception as e:
            print(f"[ERROR] Failed to empty trash: {e}")
            self.show_error(f"Failed to empty trash: {e}")

    def refresh_view(self):
        """Refresh the trash view."""
        self.load_deleted_items()

    def _format_datetime(self, dt) -> str:
        """Format datetime for display.

        Args:
            dt: DateTime object

        Returns:
            Formatted string
        """
        if dt is None:
            return "Unknown"
        return dt.strftime("%Y-%m-%d %H:%M")

    def show_error(self, message: str):
        """Show error message to user.

        Args:
            message: Error message to display
        """
        try:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Error", message)
        except Exception:
            print(f"[ERROR] {message}")
