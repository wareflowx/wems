"""Excel import view for bulk employee import."""

import threading
from pathlib import Path
from typing import Optional

import customtkinter as ctk

from ui_ctk.constants import (
    COLOR_CRITICAL,
    COLOR_SUCCESS,
    COLOR_WARNING,
    IMPORT_BUTTON_CHOOSE,
    IMPORT_BUTTON_IMPORT,
    IMPORT_BUTTON_TEMPLATE,
    IMPORT_COMPLETE,
    IMPORT_DESCRIPTION,
    IMPORT_PROGRESS,
    IMPORT_TITLE,
)
from ui_ctk.views.base_view import BaseView


class ImportView(BaseView):
    """
    Excel import view for bulk employee data import.

    Features:
    - File selection with drag-and-drop support
    - Data preview before import
    - Progress tracking during import
    - Detailed results with error messages
    - Template download
    - Thread-safe import operations
    """

    def __init__(self, master, title: str = IMPORT_TITLE):
        super().__init__(master, title=title)

        # State
        self.selected_file: Optional[Path] = None
        self.preview_data = None
        self.import_result = None
        self.is_importing = False

        # UI Components
        self.create_instructions()
        self.create_actions()
        self.create_status()

    def create_instructions(self):
        """Create instructions section."""
        instructions_frame = ctk.CTkFrame(self, height=80)
        instructions_frame.pack(side="top", fill="x", padx=10, pady=(10, 5))
        instructions_frame.pack_propagate(False)

        # Title
        title_label = ctk.CTkLabel(instructions_frame, text=IMPORT_DESCRIPTION, font=("Arial", 12))
        title_label.pack(pady=(15, 5))

        # Steps
        steps_label = ctk.CTkLabel(
            instructions_frame,
            text="1. TélEcharger le modEle  2. Remplir les donnEes  3. Choisir le fichier  4. Importer",
            font=("Arial", 10),
            text_color="gray",
        )
        steps_label.pack(pady=5)

    def create_actions(self):
        """Create action buttons section."""
        actions_frame = ctk.CTkFrame(self, height=60)
        actions_frame.pack(side="top", fill="x", padx=10, pady=5)
        actions_frame.pack_propagate(False)

        # Left side: file selection
        left_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        left_frame.pack(side="left", padx=10, pady=10)

        # Choose file button
        self.choose_btn = ctk.CTkButton(left_frame, text=IMPORT_BUTTON_CHOOSE, width=180, command=self.choose_file)
        self.choose_btn.pack(side="left", padx=5)

        # Template button
        template_btn = ctk.CTkButton(
            left_frame,
            text=IMPORT_BUTTON_TEMPLATE,
            width=180,
            fg_color=("gray70", "gray30"),
            command=self.download_template,
        )
        template_btn.pack(side="left", padx=5)

        # Right side: import button
        right_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        right_frame.pack(side="right", padx=10, pady=10)

        self.import_btn = ctk.CTkButton(
            right_frame, text=IMPORT_BUTTON_IMPORT, width=150, state="disabled", command=self.start_import
        )
        self.import_btn.pack()

        # Selected file label
        self.file_label = ctk.CTkLabel(actions_frame, text="", font=("Arial", 10), text_color="gray")
        self.file_label.pack(side="bottom", pady=(5, 10))

    def create_status(self):
        """Create status and results section."""
        # Status container
        self.status_container = ctk.CTkScrollableFrame(self)
        self.status_container.pack(side="top", fill="both", expand=True, padx=10, pady=(5, 10))

        # Welcome message
        welcome_frame = ctk.CTkFrame(self.status_container)
        welcome_frame.pack(fill="both", expand=True, padx=20, pady=20)

        welcome_label = ctk.CTkLabel(
            welcome_frame,
            text="Sélectionnez un fichier Excel pour commencer l'import",
            font=("Arial", 14),
            text_color="gray",
        )
        welcome_label.pack()

    def choose_file(self):
        """Open file dialog to select Excel file."""
        from tkinter import filedialog

        file_path = filedialog.askopenfilename(
            title="Sélectionner un fichier Excel",
            filetypes=[("Fichiers Excel", "*.xlsx"), ("Tous les fichiers", "*.*")],
        )

        if file_path:
            self.selected_file = Path(file_path)
            self.file_label.configure(text=self.selected_file.name)
            self.import_btn.configure(state="normal")

            # Preview file
            self.preview_file()

    def preview_file(self):
        """Preview selected file contents."""
        if not self.selected_file:
            return

        # Clear status container
        for widget in self.status_container.winfo_children():
            widget.destroy()

        # Show loading
        loading_label = ctk.CTkLabel(self.status_container, text="Chargement de l'aperçu...", font=("Arial", 12))
        loading_label.pack(padx=20, pady=20)

        # Load preview in background thread
        threading.Thread(target=self._load_preview, daemon=True).start()

    def _load_preview(self):
        """Load preview data (runs in background thread)."""
        try:
            import sys

            sys.path.insert(0, "src")

            from excel_import import ExcelImporter

            # Create importer
            importer = ExcelImporter(self.selected_file)

            # Validate file
            is_valid, error_msg = importer.validate_file()

            if not is_valid:
                self._show_validation_error(error_msg)
                return

            # Get preview
            preview = importer.preview(max_rows=3)
            self.preview_data = preview

            # Update UI from main thread
            self.after(0, self._display_preview, preview)

        except Exception as e:
            self.after(0, self._show_error, f"Erreur lors du chargement: {str(e)}")

    def _display_preview(self, preview):
        """Display preview data in UI."""
        # Clear loading
        for widget in self.status_container.winfo_children():
            widget.destroy()

        # Info frame
        info_frame = ctk.CTkFrame(self.status_container)
        info_frame.pack(fill="x", padx=10, pady=(10, 5))

        # Row count
        rows_label = ctk.CTkLabel(
            info_frame, text=f"Nombre de lignes: {preview['total_rows']}", font=("Arial", 12, "bold")
        )
        rows_label.pack(side="left", padx=10, pady=10)

        # Columns
        cols_text = f"Colonnes: {', '.join(preview['columns'][:5])}"
        if len(preview["columns"]) > 5:
            cols_text += f"... (+{len(preview['columns']) - 5})"
        cols_label = ctk.CTkLabel(info_frame, text=cols_text, font=("Arial", 10), text_color="gray")
        cols_label.pack(side="left", padx=10)

        # Issues warning
        if preview.get("detected_issues"):
            issues_label = ctk.CTkLabel(
                info_frame,
                text=f"⚠️ {len(preview['detected_issues'])} problèmes détectés",
                font=("Arial", 10),
                text_color=COLOR_WARNING,
            )
            issues_label.pack(side="right", padx=10)

        # Sample data frame
        if preview.get("sample_data"):
            sample_frame = ctk.CTkFrame(self.status_container)
            sample_frame.pack(fill="both", expand=True, padx=10, pady=5)

            sample_title = ctk.CTkLabel(
                sample_frame, text="Aperçu des données (3 premières lignes):", font=("Arial", 11, "bold")
            )
            sample_title.pack(pady=(10, 5), padx=10, anchor="w")

            # Display sample rows
            for i, row_data in enumerate(preview["sample_data"], 1):
                row_frame = ctk.CTkFrame(sample_frame, fg_color=("gray90", "gray20"))
                row_frame.pack(fill="x", padx=10, pady=(0, 5))

                row_label = ctk.CTkLabel(
                    row_frame,
                    text=f"Ligne {row_data['row_num']}: {self._format_sample_row(row_data)}",
                    font=("Arial", 9),
                    anchor="w",
                )
                row_label.pack(padx=10, pady=5, anchor="w")

        # Issues frame
        if preview.get("detected_issues"):
            issues_frame = ctk.CTkFrame(self.status_container)
            issues_frame.pack(fill="x", padx=10, pady=5)

            issues_title = ctk.CTkLabel(
                issues_frame, text="⚠️ Problèmes détectés:", font=("Arial", 11, "bold"), text_color=COLOR_WARNING
            )
            issues_title.pack(pady=(10, 5), padx=10, anchor="w")

            for issue in preview["detected_issues"][:10]:  # Max 10 issues
                issue_label = ctk.CTkLabel(
                    issues_frame, text=f"• {issue}", font=("Arial", 9), text_color=COLOR_WARNING, anchor="w"
                )
                issue_label.pack(padx=20, pady=2, anchor="w")

            if len(preview["detected_issues"]) > 10:
                more_label = ctk.CTkLabel(
                    issues_frame,
                    text=f"... et {len(preview['detected_issues']) - 10} autres",
                    font=("Arial", 9),
                    text_color="gray",
                    anchor="w",
                )
                more_label.pack(padx=20, pady=(5, 10), anchor="w")

    def _format_sample_row(self, row_data):
        """Format sample row for display."""
        data = row_data.get("data", {})
        parts = []

        for key in ["First Name", "Last Name", "Email", "Status", "Workspace"]:
            if key in data:
                parts.append(f"{key}={data[key]}")

        return ", ".join(parts) if parts else "(données vides)"

    def _show_validation_error(self, error_msg):
        """Show file validation error."""
        for widget in self.status_container.winfo_children():
            widget.destroy()

        error_frame = ctk.CTkFrame(self.status_container)
        error_frame.pack(fill="both", expand=True, padx=20, pady=20)

        error_label = ctk.CTkLabel(
            error_frame, text=f"❌ Erreur de validation\n\n{error_msg}", font=("Arial", 12), text_color=COLOR_CRITICAL
        )
        error_label.pack()

    def _show_error(self, message):
        """Show error message."""
        for widget in self.status_container.winfo_children():
            widget.destroy()

        error_frame = ctk.CTkFrame(self.status_container)
        error_frame.pack(fill="both", expand=True, padx=20, pady=20)

        error_label = ctk.CTkLabel(error_frame, text=f"❌ {message}", font=("Arial", 12), text_color=COLOR_CRITICAL)
        error_label.pack()

    def start_import(self):
        """Start import process in background thread."""
        if not self.selected_file or self.is_importing:
            return

        self.is_importing = True
        self.import_btn.configure(state="disabled")

        # Clear status and show progress
        for widget in self.status_container.winfo_children():
            widget.destroy()

        # Progress frame
        self.progress_frame = ctk.CTkFrame(self.status_container)
        self.progress_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Progress label
        self.progress_label = ctk.CTkLabel(self.progress_frame, text=IMPORT_PROGRESS, font=("Arial", 12))
        self.progress_label.pack(pady=(10, 5))

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, width=400)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)

        # Status label
        self.status_label = ctk.CTkLabel(
            self.progress_frame, text="Préparation...", font=("Arial", 10), text_color="gray"
        )
        self.status_label.pack(pady=(0, 10))

        # Start import in background
        threading.Thread(target=self._run_import, daemon=True).start()

    def _run_import(self):
        """Run import process (background thread)."""
        try:
            import sys

            sys.path.insert(0, "src")

            from excel_import import ExcelImporter

            # Create importer
            importer = ExcelImporter(self.selected_file)

            # Validate again (file might have changed)
            is_valid, error_msg = importer.validate_file()
            if not is_valid:
                self.after(0, self._show_error, error_msg)
                self.after(0, self._import_finished, False)
                return

            # Progress callback
            def update_progress(current, total):
                percentage = current / total if total > 0 else 0
                self.after(0, self._update_progress, percentage, current, total)

            # Run import
            result = importer.import_employees(progress_callback=update_progress)
            self.import_result = result

            # Show results
            self.after(0, self._display_results, result)
            self.after(0, self._import_finished, True)

        except Exception as e:
            self.after(0, self._show_error, f"Erreur lors de l'import: {str(e)}")
            self.after(0, self._import_finished, False)

    def _update_progress(self, percentage, current, total):
        """Update progress bar."""
        self.progress_bar.set(percentage)
        self.status_label.configure(text=f"{current} / {total} lignes traitées")

    def _display_results(self, result):
        """Display import results."""
        # Clear progress frame
        self.progress_frame.destroy()

        # Results frame
        results_frame = ctk.CTkFrame(self.status_container)
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Header
        header_text = IMPORT_COMPLETE
        header_color = COLOR_SUCCESS if result.success_rate >= 50 else COLOR_WARNING

        header_label = ctk.CTkLabel(
            results_frame, text=header_text, font=("Arial", 14, "bold"), text_color=header_color
        )
        header_label.pack(pady=(10, 15))

        # Statistics
        stats_frame = ctk.CTkFrame(results_frame, fg_color=("gray90", "gray20"))
        stats_frame.pack(fill="x", padx=15, pady=(0, 15))

        # Success
        success_label = ctk.CTkLabel(
            stats_frame, text=f"✓ Réussies: {result.successful}", font=("Arial", 12), text_color=COLOR_SUCCESS
        )
        success_label.pack(side="left", padx=15, pady=10)

        # Failed
        failed_label = ctk.CTkLabel(
            stats_frame, text=f"✗ Échouées: {result.failed}", font=("Arial", 12), text_color=COLOR_CRITICAL
        )
        failed_label.pack(side="left", padx=15, pady=10)

        # Skipped
        skipped_label = ctk.CTkLabel(
            stats_frame, text=f"⊘ Ignorées: {result.skipped}", font=("Arial", 12), text_color="gray"
        )
        skipped_label.pack(side="left", padx=15, pady=10)

        # Duration
        duration_text = f"Durée: {result.duration:.1f}s"
        duration_label = ctk.CTkLabel(stats_frame, text=duration_text, font=("Arial", 10), text_color="gray")
        duration_label.pack(side="right", padx=15, pady=10)

        # Errors section
        if result.errors:
            errors_frame = ctk.CTkFrame(results_frame)
            errors_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

            errors_title = ctk.CTkLabel(
                errors_frame,
                text=f"Erreurs ({len(result.errors)}):",
                font=("Arial", 11, "bold"),
                text_color=COLOR_CRITICAL,
            )
            errors_title.pack(pady=(10, 5), anchor="w", padx=10)

            # Scrollable error list
            error_scroll = ctk.CTkScrollableFrame(errors_frame, height=150)
            error_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

            for error in result.errors[:50]:  # Max 50 errors
                error_text = str(error)
                error_label = ctk.CTkLabel(
                    error_scroll, text=f"• {error_text}", font=("Arial", 9), text_color=COLOR_CRITICAL, anchor="w"
                )
                error_label.pack(anchor="w", pady=2)

            if len(result.errors) > 50:
                more_label = ctk.CTkLabel(
                    error_scroll,
                    text=f"... et {len(result.errors) - 50} autres erreurs",
                    font=("Arial", 9),
                    text_color="gray",
                    anchor="w",
                )
                more_label.pack(anchor="w", pady=(5, 0))

    def _import_finished(self, success):
        """Import finished callback."""
        self.is_importing = False
        if success:
            # Re-enable import button but also refresh parent views
            self.import_btn.configure(state="normal")

            # Trigger employee list refresh
            if hasattr(self.master_window, "refresh_employee_list"):
                self.master_window.refresh_employee_list()

            print(f"[INFO] Import completed: {self.import_result.successful} employees imported")
        else:
            self.import_btn.configure(state="normal")

    def download_template(self):
        """Download Excel template."""
        from tkinter import filedialog

        # Ask save location
        file_path = filedialog.asksaveasfilename(
            title="Enregistrer le modèle",
            defaultextension=".xlsx",
            initialfile="employee_import_template.xlsx",
            filetypes=[("Fichiers Excel", "*.xlsx"), ("Tous les fichiers", "*.*")],
        )

        if file_path:
            try:
                import sys

                sys.path.insert(0, "src")

                from excel_import import ExcelTemplateGenerator

                # Generate template
                generator = ExcelTemplateGenerator()
                generator.generate_template(Path(file_path))

                # Show success message
                self._show_template_success(Path(file_path))

            except Exception as e:
                self._show_error(f"Erreur lors de la génération du modèle: {str(e)}")

    def _show_template_success(self, file_path):
        """Show template generation success message."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Modèle généré")
        dialog.geometry("400x150")

        # Center on screen
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (150 // 2)
        dialog.geometry(f"400x150+{x}+{y}")

        # Message
        msg_label = ctk.CTkLabel(dialog, text=f"✓ Modèle généré avec succès!\n\n{file_path.name}", font=("Arial", 12))
        msg_label.pack(pady=30, padx=20)

        # Close button
        close_btn = ctk.CTkButton(dialog, text="Fermer", width=100, command=dialog.destroy)
        close_btn.pack(pady=10)

    def refresh(self):
        """Refresh view (called by parent)."""
        # Reset state
        self.selected_file = None
        self.preview_data = None
        self.import_result = None
        self.is_importing = False

        # Reset UI
        self.file_label.configure(text="")
        self.import_btn.configure(state="disabled")

        # Clear status container
        for widget in self.status_container.winfo_children():
            widget.destroy()

        # Show welcome message
        welcome_frame = ctk.CTkFrame(self.status_container)
        welcome_frame.pack(fill="both", expand=True, padx=20, pady=20)

        welcome_label = ctk.CTkLabel(
            welcome_frame,
            text="Sélectionnez un fichier Excel pour commencer l'import",
            font=("Arial", 14),
            text_color="gray",
        )
        welcome_label.pack()
