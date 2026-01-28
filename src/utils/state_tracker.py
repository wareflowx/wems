"""Form state manager for tracking unsaved changes.

This module provides functionality to track form state changes and detect
when users have unsaved modifications, preventing accidental data loss.
"""

import customtkinter as ctk
from typing import Any, Dict, Optional


class FormStateManager:
    """Manages form state for detecting unsaved changes.

    This class tracks the initial and current state of form fields
    to detect when the user has made unsaved modifications.

    Features:
    - Automatic field state capture
    - Change detection for StringVar, IntVar, BooleanVar
    - State reset after save
    - Unsaved indicator management
    """

    def __init__(self, form):
        """Initialize state manager for a form.

        Args:
            form: The form dialog instance to manage
        """
        self.form = form
        self.initial_state: Dict[str, Any] = {}
        self.current_state: Dict[str, Any] = {}
        self.has_unsaved_changes: bool = False
        self._tracked_vars: Dict[str, ctk.Variable] = {}
        self._explicitly_tracked: Dict[str, ctk.Variable] = {}

    def track_variable(self, name: str, var: ctk.Variable) -> None:
        """Explicitly track a form variable for change detection.

        Args:
            name: Variable name/identifier
            var: The CustomTkinter variable (StringVar, IntVar, etc.)
        """
        self._explicitly_tracked[name] = var
        try:
            self.initial_state[name] = var.get()
        except Exception:
            self.initial_state[name] = None

    def capture_initial_state(self) -> None:
        """Capture the initial state of all tracked form variables.

        This should be called after form fields are created but before
        any user interaction.
        """
        # First, capture explicitly tracked variables
        for name, var in self._explicitly_tracked.items():
            try:
                self.initial_state[name] = var.get()
                self._tracked_vars[name] = var
            except Exception:
                # Variable might not be initialized yet, skip it
                pass

        # Then, auto-discover other tkinter variables in the form
        for attr_name in dir(self.form):
            if attr_name.startswith('_'):
                continue

            # Skip already explicitly tracked
            if attr_name in self._tracked_vars:
                continue

            attr = getattr(self.form, attr_name, None)
            if attr is None:
                continue

            # Track StringVar, IntVar, BooleanVar, DoubleVar
            if isinstance(attr, (ctk.StringVar, ctk.IntVar, ctk.BooleanVar, ctk.DoubleVar)):
                try:
                    self.initial_state[attr_name] = attr.get()
                    self._tracked_vars[attr_name] = attr
                except Exception:
                    # Variable might not be initialized yet, skip it
                    pass

    def check_for_changes(self) -> bool:
        """Check if form has unsaved changes by comparing states.

        Returns:
            True if current state differs from initial state, False otherwise
        """
        self.current_state = {}

        # Capture current state
        for attr_name, var in self._tracked_vars.items():
            try:
                self.current_state[attr_name] = var.get()
            except Exception:
                # Variable might be destroyed, skip it
                pass

        # Compare states
        return self.current_state != self.initial_state

    def update_has_unsaved(self) -> bool:
        """Update and return the unsaved changes status.

        Returns:
            True if form has unsaved changes, False otherwise
        """
        self.has_unsaved_changes = self.check_for_changes()
        return self.has_unsaved_changes

    def mark_as_saved(self) -> None:
        """Mark form as saved by updating initial state to current state.

        This should be called after a successful save operation.
        """
        self.has_unsaved_changes = False
        self.initial_state = self.current_state.copy()

    def get_changed_fields(self) -> Dict[str, tuple]:
        """Get list of fields that have changed.

        Returns:
            Dictionary mapping field names to (old_value, new_value) tuples
        """
        changed = {}
        for attr_name in self._tracked_vars:
            if attr_name in self.initial_state and attr_name in self.current_state:
                old_val = self.initial_state[attr_name]
                new_val = self.current_state[attr_name]
                if old_val != new_val:
                    changed[attr_name] = (old_val, new_val)
        return changed

    def reset(self) -> None:
        """Reset the state manager to initial conditions.

        This clears all tracked state and marks form as having no changes.
        """
        self.initial_state = {}
        self.current_state = {}
        self.has_unsaved_changes = False
        self._tracked_vars = {}
        self._explicitly_tracked = {}
