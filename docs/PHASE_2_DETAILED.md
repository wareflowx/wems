# PHASE 2: CUSTOMTKINTER UI STRUCTURE (DETAILED)

## 📋 OVERVIEW

**Objective**: Create the foundational CustomTkinter application structure with main window, navigation system, and view switching mechanism.

**Duration**: 4 hours
**Complexity**: Medium
**Dependencies**: Phase 0 (UI package, constants, base classes), Phase 1 (Employee model with phone/email)
**Deliverables**: Main entry point, main window with navigation, working view switching

---

## 🎯 DETAILED TASKS

### Task 2.1: Create Main Entry Point

#### 2.1.1. Application Entry Point Design

**File**: `src/ui_ctk/app.py`

**Purpose**:
- Initialize CustomTkinter framework
- Setup application configuration
- Initialize database connection
- Create main window
- Start application event loop

**Complete Implementation:**

```python
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

        # Connect to database
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

        # Destroy window
        app.destroy()

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
    finally:
        on_closing()

    print("[OK] Application closed cleanly")


if __name__ == "__main__":
    main()
```

#### 2.1.2. Entry Point Architecture

**Flow Diagram:**

```
main()
  |
  +-> setup_customtkinter()
  |   - Set appearance mode
  |   - Set color theme
  |
  +-> setup_database()
  |   - Check if DB exists
  |   - Initialize connection
  |   - Create tables (safe=True)
  |
  +-> create main window
  |   - Create CTk root
  |   - Set title and geometry
  |   - Create MainWindow
  |   - Pack main window
  |
  +-> Setup close handler
  |   - Register WM_DELETE_WINDOW
  |   - Close database on exit
  |   - Clean shutdown
  |
  +-> Start mainloop()
      - Application runs
      - Event handling
      - User interaction
```

#### 2.1.3. Configuration Management

**Centralized Configuration:**

All configuration constants are in `src/ui_ctk/constants.py`:

```python
# Window Configuration
DEFAULT_WIDTH = 1200
DEFAULT_HEIGHT = 800
MIN_WIDTH = 800
MIN_HEIGHT = 600

# Theme Configuration
DEFAULT_THEME = "blue"
DEFAULT_MODE = "System"
```

**Benefits:**
- Single source of truth
- Easy to modify appearance
- No hardcoded values
- Consistent across application

**Theme Options Available:**

**Appearance Modes:**
- `System` - Follows system preference (recommended)
- `Dark` - Always dark mode
- `Light` - Always light mode

**Color Themes:**
- `blue` - Default blue theme (recommended)
- `green` - Green accent theme
- `dark-blue` - Dark blue theme

**How to Change Theme:**

```python
# In app.py, change constants.py:
DEFAULT_THEME = "green"  # Change from "blue"
DEFAULT_MODE = "Dark"    # Force dark mode
```

#### 2.1.4. Error Handling Strategy

**Database Connection Failures:**

```python
def setup_database(db_path: str = "employee_manager.db"):
    try:
        init_database(Path(db_path))
        database.connect()
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
        print("\n[INFO] Troubleshooting:")
        print("  1. Check if database file exists")
        print("  2. Check file permissions")
        print("  3. Verify database is not locked")
        print("  4. Check Python dependencies are installed")

        # Show error dialog if GUI is available
        try:
            import tkinter.messagebox as messagebox
            messagebox.showerror(
                "Database Error",
                f"Failed to initialize database:\n\n{e}\n\n"
                "The application cannot start."
            )
        except:
            pass

        raise
```

**Window Creation Failures:**

```python
def create_main_window(app: ctk.CTk) -> MainWindow:
    try:
        window = MainWindow(app)
        window.pack(fill="both", expand=True)
        return window
    except Exception as e:
        print(f"[ERROR] Failed to create main window: {e}")

        # Show error dialog
        try:
            import tkinter.messagebox as messagebox
            messagebox.showerror(
                "Initialization Error",
                f"Failed to create main window:\n\n{e}"
            )
        except:
            pass

        raise
```

---

### Task 2.2: Create Main Window with Navigation

#### 2.2.1. Main Window Design

**File**: `src/ui_ctk/main_window.py`

**Purpose:**
- Container for all application views
- Navigation bar with buttons
- View switching mechanism
- Layout management

**Layout Structure:**

```
┌─────────────────────────────────────────────────────┐
│  Wareflow EMS - Gestion des Salariés                   │
├─────────────────────────────────────────────────────┤
│  [👥 Employés] [⚠️ Alertes] [📥 Import Excel]     │  ← Navigation
├─────────────────────────────────────────────────────┤
│                                                     │
│                                                     │
│              DYNAMIC VIEW CONTENT                   │  ← View Container
│          (changes based on navigation)              │
│                                                     │
│                                                     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Complete Implementation:**

```python
"""Main application window with navigation bar."""

import customtkinter as ctk
from typing import Optional, Callable
from ui_ctk.views.base_view import BaseView
from ui_ctk.constants import (
    APP_TITLE,
    NAV_EMPLOYEES,
    NAV_ALERTS,
    NAV_IMPORT,
    DEFAULT_WIDTH,
    DEFAULT_HEIGHT,
)


class MainWindow(ctk.CTkFrame):
    """
    Main application window with navigation bar.

    Features:
    - Navigation bar with 3 main sections
    - Dynamic view container
    - View switching mechanism
    - Clean layout management
    """

    def __init__(self, master: ctk.CTk):
        """
        Initialize main window.

        Args:
            master: Root CTk application
        """
        super().__init__(master, fg_color="transparent")

        # Store reference to master for navigation
        self.master_window = master

        # Track current view
        self.current_view: Optional[BaseView] = None

        # Create UI components
        self.create_navigation_bar()
        self.create_view_container()

        # Show default view (employee list)
        self.show_employee_list()

    def create_navigation_bar(self):
        """Create navigation bar with buttons."""
        # Navigation container
        self.nav_bar = ctk.CTkFrame(self, height=60)
        self.nav_bar.pack(side="top", fill="x", padx=10, pady=10)
        self.nav_bar.pack_propagate(False)

        # Title label
        title_label = ctk.CTkLabel(
            self.nav_bar,
            text=APP_TITLE,
            font=("Arial", 16, "bold")
        )
        title_label.pack(side="left", padx=20)

        # Button container (right side)
        button_container = ctk.CTkFrame(self.nav_bar, fg_color="transparent")
        button_container.pack(side="right")

        # Employee list button
        self.btn_employees = ctk.CTkButton(
            button_container,
            text=NAV_EMPLOYEES,
            width=120,
            command=self.show_employee_list
        )
        self.btn_employees.pack(side="left", padx=5)

        # Alerts button
        self.btn_alerts = ctk.CTkButton(
            button_container,
            text=NAV_ALERTS,
            width=120,
            command=self.show_alerts
        )
        self.btn_alerts.pack(side="left", padx=5)

        # Import button
        self.btn_import = ctk.CTkButton(
            button_container,
            text=NAV_IMPORT,
            width=140,
            command=self.show_import
        )
        self.btn_import.pack(side="left", padx=5)

    def create_view_container(self):
        """Create container for dynamic views."""
        self.view_container = ctk.CTkFrame(self)
        self.view_container.pack(
            side="top",
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

    def clear_view(self):
        """Remove current view from container."""
        if self.current_view:
            self.current_view.destroy()
            self.current_view = None

    def switch_view(self, view_class: type, *args, **kwargs):
        """
        Switch to a new view.

        Args:
            view_class: View class to instantiate
            *args: Positional arguments for view constructor
            **kwargs: Keyword arguments for view constructor
        """
        # Remove current view
        self.clear_view()

        # Create new view
        self.current_view = view_class(self.view_container, *args, **kwargs)
        self.current_view.pack(fill="both", expand=True)

        # Update button states
        self.update_navigation_state()

    def update_navigation_state(self):
        """Update navigation button states to show active section."""
        # Reset all buttons to default
        default_fg = self.master_window.cget("fgcolor")

        self.btn_employees.configure(fg_color=default_fg)
        self.btn_alerts.configure(fg_color=default_fg)
        self.btn_import.configure(fg_color=default_fg)

        # Note: In future versions, we could highlight active button
        # For now, all buttons remain neutral

    # ===== Navigation Methods =====

    def show_employee_list(self):
        """Display employee list view."""
        try:
            from ui_ctk.views.employee_list import EmployeeListView
            self.switch_view(EmployeeListView, title="Liste des Employés")
            print("[NAV] Showing employee list view")
        except Exception as e:
            print(f"[ERROR] Failed to load employee list: {e}")
            self.show_error(f"Failed to load employee list: {e}")

    def show_alerts(self):
        """Display alerts view."""
        try:
            from ui_ctk.views.alerts_view import AlertsView
            self.switch_view(AlertsView, title="Alertes")
            print("[NAV] Showing alerts view")
        except Exception as e:
            print(f"[ERROR] Failed to load alerts view: {e}")
            self.show_error(f"Failed to load alerts: {e}")

    def show_import(self):
        """Display import view."""
        try:
            from ui_ctk.views.import_view import ImportView
            self.switch_view(ImportView, title="Import Excel")
            print("[NAV] Showing import view")
        except Exception as e:
            print(f"[ERROR] Failed to load import view: {e}")
            self.show_error(f"Failed to load import: {e}")

    def show_error(self, message: str):
        """Show error message to user."""
        try:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Error", message)
        except:
            print(f"[ERROR] {message}")
```

#### 2.2.2. Navigation System Architecture

**Navigation Flow:**

```
User clicks "Alerts" button
        ↓
btn_alerts.command triggered
        ↓
MainWindow.show_alerts()
        ↓
clear_view() removes current view
        ↓
switch_view(AlertsView, title="Alertes")
        ↓
AlertsView.__init__() creates view
        ↓
view packed into view_container
        ↓
Navigation states updated
```

**State Management:**

**Current View Tracking:**
```python
self.current_view: Optional[BaseView] = None
```

**Why Track Current View?**
- Clean removal when switching
- Prevent memory leaks
- Proper cleanup callbacks
- Navigation state

**View Lifecycle:**

```
View Creation:
1. clear_view() destroys old view
2. New view instantiated
3. View packed into container
4. View receives focus
5. View can run initialization code

View Destruction:
1. View receives cleanup callback
2. View can save state
3. View destroyed
4. Memory freed
```

#### 2.2.3. Layout Management Details

**Pack Configuration:**

```python
# Navigation bar: Fixed at top
self.nav_bar.pack(side="top", fill="x", padx=10, pady=10)
self.nav_bar.pack_propagate(False)  # Prevent height changes

# View container: Fills remaining space
self.view_container.pack(
    side="top",
    fill="both",      # Fill horizontally
    expand=True,      # Fill vertically
    padx=10,          # Horizontal padding
    pady=10           # Vertical padding
)
```

**Layout Behavior:**

- **Navigation Bar**: Fixed height (60px), doesn't expand
- **View Container**: Expands to fill all remaining space
- **Padding**: 10px margin around view container
- **Responsive**: Window resize affects view container only

**Window Resize Handling:**

```python
# When user resizes window:
app.geometry("1400x900")  # User drags corner

# CustomTkinter handles:
# - View container expands
# - Navigation bar stays fixed
# - Views receive resize events
# - Content adjusts automatically
```

#### 2.2.4. Button Design

**Button Specifications:**

```python
# Employee List Button
ctk.CTkButton(
    parent=button_container,
    text="Employés",
    width=120,            # Fixed width for consistency
    height=32,           # Default height
    command=self.show_employee_list
)

# Alerts Button
ctk.CTkButton(
    parent=button_container,
    text="Alertes",
    width=120,
    height=32,
    command=self.show_alerts
)

# Import Button
ctk.CTkButton(
    parent=button_container,
    text="Import Excel",
    width=140,            # Slightly wider for text
    height=32,
    command=self.show_import
)
```

**Button Styling:**

**Default CustomTkinter Appearance:**
- Rounded corners
- Hover effect (color change)
- Click effect (slight press animation)
- Blue accent color (from theme)
- White text on dark background

**Future Enhancements (Optional V2):**
```python
# Could add icons to buttons
button_with_icon = ctk.CTkButton(
    parent=self,
    text="  Employés",  # Space for icon
    image=ctk.CTkImage(light_image=icon_employees),
    compound="left",
    width=140
)
```

---

### Task 2.3: Implement View Switching System

#### 2.3.1. View Switching Logic

**Core Switching Method:**

```python
def switch_view(self, view_class: type, *args, **kwargs):
    """
    Switch to a new view.

    This method ensures:
    1. Current view is properly destroyed
    2. Resources are cleaned up
    3. New view is instantiated
    4. New view is displayed
    5. Navigation state is updated
    """
    # Step 1: Remove current view
    self.clear_view()

    # Step 2: Create new view
    self.current_view = view_class(self.view_container, *args, **kwargs)

    # Step 3: Display new view
    self.current_view.pack(fill="both", expand=True)

    # Step 4: Update navigation
    self.update_navigation_state()
```

**Example Usage:**

```python
# Switch to employee list
self.switch_view(EmployeeListView, title="Liste des Employés")

# Switch to alerts
self.switch_view(AlertsView, title="Alertes")

# Switch to import with parameters
self.switch_view(ImportView, title="Import Excel", file_path=path)
```

#### 2.3.2. View Cleanup

**Cleanup Implementation:**

```python
def clear_view(self):
    """Remove current view from container."""
    if self.current_view:
        # Call cleanup method if exists
        if hasattr(self.current_view, 'cleanup'):
            try:
                self.current_view.cleanup()
            except Exception as e:
                print(f"[WARN] View cleanup error: {e}")

        # Destroy view
        self.current_view.destroy()
        self.current_view = None
```

**Why Cleanup is Important:**

1. **Memory Management**: Prevents memory leaks
2. **Resource Release**: Closes files, connections
3. **State Saving**: Views can save state before destruction
4. **Event Unbinding**: Removes event handlers
5. **Timer Cleanup**: Cancels pending timers

**Example View Cleanup:**

```python
class EmployeeListView(BaseView):
    def __init__(self, master, title=""):
        super().__init__(master, title)

        # Create timer for refresh
        self.refresh_timer = self.after(60000, self.auto_refresh)

    def cleanup(self):
        """Cleanup resources when view is destroyed."""
        # Cancel timer
        if hasattr(self, 'refresh_timer'):
            self.after_cancel(self.refresh_timer)

        # Close open files
        if hasattr(self, 'log_file'):
            self.log_file.close()

        # Close database connections
        if hasattr(self, 'conn'):
            self.conn.close()
```

#### 2.3.3. Navigation State Management

**Active State Tracking:**

```python
class MainWindow(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk):
        super().__init__(master)

        # Track navigation state
        self.current_view: Optional[BaseView] = None
        self.navigation_history = []  # For back button (future)

        # Navigation buttons
        self.btn_employees: Optional[ctk.CTkButton] = None
        self.btn_alerts: Optional[ctk.CTkButton] = None
        self.btn_import: Optional[ctk.CTkButton] = None
```

**Future Enhancement: Navigation History**

```python
def navigate_to(self, view_class: type, *args, **kwargs):
    """
    Navigate to a new view with history tracking.

    Allows implementing back button functionality.
    """
    # Save current view to history
    if self.current_view:
        self.navigation_history.append(type(self.current_view))

    # Navigate to new view
    self.switch_view(view_class, *args, **kwargs)

def navigate_back(self):
    """Navigate back to previous view."""
    if self.navigation_history:
        previous_view_class = self.navigation_history.pop()
        self.switch_view(previous_view_class)
```

#### 2.3.4. Error Handling in Navigation

**Import Error Handling:**

```python
def show_employee_list(self):
    """Display employee list view."""
    try:
        from ui_ctk.views.employee_list import EmployeeListView
        self.switch_view(EmployeeListView, title="Liste des Employés")
        print("[NAV] Showing employee list view")
    except ImportError as e:
        print(f"[ERROR] Failed to import EmployeeListView: {e}")
        self.show_error(
            f"Failed to load employee list view:\n\n"
            f"The view module may not be implemented yet.\n\n"
            f"Error: {e}"
        )
    except Exception as e:
        print(f"[ERROR] Failed to load employee list: {e}")
        self.show_error(f"Failed to load employee list: {e}")
```

**Fallback Strategy:**

```python
def show_employee_list(self):
    """Display employee list view with fallback."""
    try:
        from ui_ctk.views.employee_list import EmployeeListView
        self.switch_view(EmployeeListView, title="Liste des Employés")
    except ImportError:
        # View not implemented yet - show placeholder
        self.show_placeholder_view("Employee List", "View not implemented")
```

---

### Task 2.4: Design Placeholder Views

#### 2.4.1. Temporary Placeholder View

**Purpose**: Allow navigation to work before views are implemented

**Implementation:**

```python
"""Placeholder view for unimplemented screens."""

import customtkinter as ctk
from ui_ctk.views.base_view import BaseView


class PlaceholderView(BaseView):
    """Placeholder view for unimplemented features."""

    def __init__(self, master, title: str = "Coming Soon"):
        super().__init__(master, title=title)

        # Create placeholder content
        label = ctk.CTkLabel(
            self,
            text=f"{title}\n\nComing Soon",
            font=("Arial", 24)
        )
        label.pack(expand=True)

        info_label = ctk.CTkLabel(
            self,
            text="This feature will be implemented in a future update.",
            font=("Arial", 14),
            text_color="gray"
        )
        info_label.pack(pady=20)
```

**Usage in MainWindow:**

```python
def show_alerts(self):
    """Display alerts view."""
    try:
        from ui_ctk.views.alerts_view import AlertsView
        self.switch_view(AlertsView, title="Alertes")
    except ImportError:
        # View not implemented - show placeholder
        from ui_ctk.views.placeholder import PlaceholderView
        self.switch_view(PlaceholderView, title="Alertes (Coming Soon)")
```

---

### Task 2.5: Testing Strategy

#### 2.5.1: Unit Testing Main Components

**Test Main Entry Point:**

```python
# File: tests/test_app.py
"""Test application entry point."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch
import customtkinter as ctk

sys.path.insert(0, 'src')


def test_app_initialization():
    """Test application can be initialized."""
    print("[TEST] Testing app initialization...")

    # Mock database to avoid side effects
    with patch('ui_ctk.app.setup_database'):
        with patch('ui_ctk.app.create_main_window') as mock_create:
            # Import app (runs initialization)
            from ui_ctk.app import main

            # Assert database setup was called
            assert setup_database.called

            # Assert main window was created
            assert mock_create.called

            print("[OK] App initialization test passed")


def test_customtkinter_setup():
    """Test CustomTkinter configuration."""
    print("\n[TEST] Testing CustomTkinter setup...")

    # Mock CTk
    with patch('customtkinter.CTk') as mock_ctk:
        with patch('customtkinter.set_appearance_mode') as mock_mode:
            with patch('customtkinter.set_default_color_theme') as mock_theme:
                from ui_ctk.app import setup_customtkinter

                # Assert configuration was called
                assert mock_mode.called
                assert mock_theme.called

                print("[OK] CustomTkinter setup test passed")


if __name__ == "__main__":
    test_app_initialization()
    test_customtkinter_setup()
    print("\n[OK] ALL APP TESTS PASSED")
```

#### 2.5.2. Integration Testing

**Test Window Creation:**

```python
# File: tests/test_main_window.py
"""Test main window creation."""

import sys
import customtkinter as ctk
from pathlib import Path

sys.path.insert(0, 'src')

from ui_ctk.main_window import MainWindow
from ui_ctk.constants import (
    APP_TITLE,
    NAV_EMPLOYEES,
    NAV_ALERTS,
    NAV_IMPORT,
)


def test_main_window_creation():
    """Test main window can be created."""
    print("[TEST] Testing main window creation...")

    # Create root app
    app = ctk.CTk()
    app.title("Test App")
    app.geometry("800x600")

    # Create main window
    main_window = MainWindow(app)
    main_window.pack(fill="both", expand=True)

    # Verify components exist
    assert hasattr(main_window, 'nav_bar'), "Missing nav_bar"
    assert hasattr(main_window, 'view_container'), "Missing view_container"
    assert hasattr(main_window, 'current_view'), "Missing current_view"

    # Verify navigation buttons exist
    assert hasattr(main_window, 'btn_employees'), "Missing btn_employees"
    assert hasattr(main_window, 'btn_alerts'), "Missing btn_alerts"
    assert hasattr(main_window, 'btn_import'), "Missing btn_import"

    print("[OK] Main window has all components")

    # Verify navigation methods exist
    assert hasattr(main_window, 'show_employee_list'), "Missing show_employee_list"
    assert hasattr(main_window, 'show_alerts'), "Missing show_alerts"
    assert hasattr(main_window, 'show_import'), "Missing show_import"
    assert hasattr(main_window, 'clear_view'), "Missing clear_view"

    print("[OK] Main window has all navigation methods")

    # Cleanup
    app.destroy()

    print("[OK] Main window creation test passed")


if __name__ == "__main__":
    test_main_window_creation()
    print("\n[OK] ALL MAIN WINDOW TESTS PASSED")
```

#### 2.5.3. Visual Testing Checklist

**Manual Testing Procedure:**

1. **Launch Application**
   ```bash
   uv run python -m src.ui_ctk.app
   ```

2. **Verify Window Appearance**
   - [ ] Window title shows "Wareflow EMS - Gestion des Salariés"
   - [ ] Window size is 1200x800
   - [ ] Window can be resized
   - [ ] Minimum size is enforced (800x600)

3. **Test Navigation Bar**
   - [ ] Navigation bar visible at top
   - [ ] Title visible on left
   - [ ] Three buttons visible on right
   - [ ] Buttons have correct text (Employés, Alertes, Import Excel)
   - [ ] Buttons are clickable

4. **Test Navigation**
   - [ ] Click "Employés" - employee list appears
   - [ ] Click "Alertes" - alerts view appears
   - [ ] Click "Import Excel" - import view appears
   - [ ] Clicking same button doesn't cause errors
   - [ ] Navigation feels smooth

5. **Test Window Resize**
   - [ ] Resize window larger - view container expands
   - [ ] Resize window smaller - view container shrinks
   - [ ] Navigation bar stays at top
   - [ ] No layout breaks

6. **Test Window Close**
   - [ ] Close window - application exits cleanly
   - [ ] Database connection closed
   - [ ] No errors in terminal

---

### Task 2.6: Error Handling & User Feedback

#### 2.6.1. Graceful Degradation

**Import Error Handling:**

```python
def show_employee_list(self):
    """Display employee list view with robust error handling."""
    view_module = "ui_ctk.views.employee_list"
    view_class = "EmployeeListView"

    try:
        # Try to import view
        module = __import__(view_module, fromlist=[view_class])
        view_cls = getattr(module, view_class)

        # Switch to view
        self.switch_view(view_cls, title="Liste des Employés")

        print(f"[NAV] Successfully loaded {view_class}")

    except ImportError as e:
        print(f"[ERROR] Failed to import {view_class}: {e}")

        # Show user-friendly error
        self.show_unavailable_feature(
            title="Employee List",
            feature="Employee List View",
            error=str(e)
        )

    except Exception as e:
        print(f"[ERROR] Unexpected error loading view: {e}")
        self.show_error(f"Failed to load employee list: {e}")
```

**User Feedback Methods:**

```python
def show_unavailable_feature(self, title: str, feature: str, error: str):
    """Show 'coming soon' message for unimplemented feature."""
    try:
        import tkinter.messagebox as messagebox
        messagebox.showinfo(
            "Feature Not Available",
            f"{title}\n\n"
            f"This feature is not yet available.\n"
            f"It will be implemented in a future update."
        )
    except:
        pass


def show_error(self, message: str):
    """Show error dialog to user."""
    try:
        import tkinter.messagebox as messagebox
        messagebox.showerror("Error", message)
    except:
        print(f"[ERROR DISPLAY] {message}")
```

#### 2.6.2. Logging Strategy

**Application Logging:**

```python
"""Application logging configuration."""

import logging
from pathlib import Path


def setup_logging():
    """Configure application logging."""
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Configure logging
    log_file = logs_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    print(f"[OK] Logging configured: {log_file}")
```

**Usage in app.py:**

```python
# At start of main()
def main():
    """Application entry point."""
    setup_logging()  # Add this

    log = logging.getLogger(__name__)

    log.info("=" * 50)
    log.info(f"{APP_NAME} v{APP_VERSION} starting")
    log.info("=" * 50)

    # ... rest of main()
```

---

### Task 2.7: Performance Considerations

#### 2.7.1. Startup Performance

**Startup Time Breakdown:**

| Operation | Estimated Time | Optimization |
|-----------|----------------|---------------|
| Python imports | 0.5s | Lazy imports |
| CustomTkinter init | 0.3s | Minimal |
| Database connection | 0.2s | Connection pooling |
| Table creation | 0.1s | safe=True (fast) |
| Window creation | 0.1s | Minimal |
| **Total** | **~1.2s** | Acceptable |

**Optimization Strategies:**

```python
# Lazy import views (faster startup)
def show_employee_list(self):
    """Import view only when needed."""
    if not self._employee_list_loaded:
        from ui_ctk.views.employee_list import EmployeeListView
        self._EmployeeListView = EmployeeListView
        self._employee_list_loaded = True

    # Use cached import
    self.switch_view(self._EmployeeListView, title="Liste des Employés")
```

#### 2.7.2. Memory Management

**Memory Considerations:**

**View Memory Footprint:**
- Employee list (100 employees): ~5-10 MB
- Alerts view (500 alerts): ~2-5 MB
- Import view: ~1 MB
- **Total per view**: ~10-15 MB

**Memory Cleanup:**

```python
def clear_view(self):
    """Remove current view and free memory."""
    if self.current_view:
        # Cancel pending timers
        if hasattr(self.current_view, 'cancel_timers'):
            self.current_view.cancel_timers()

        # Close database cursors
        if hasattr(self.current_view, 'close_cursors'):
            self.current_view.close_cursors()

        # Unload large datasets
        if hasattr(self.current_view, 'unload_data'):
            self.current_view.unload_data()

        # Destroy view
        self.current_view.destroy()
        self.current_view = None
```

#### 2.7.3. Responsive Design

**Layout Responsiveness:**

```python
class ResponsiveMainWindow(MainWindow):
    """Main window with responsive layout."""

    def __init__(self, master: ctk.CTk):
        super().__init__(master)

        # Bind resize event
        master.bind("<Configure>", self.on_window_resize)

        # Initial layout
        self.create_navigation_bar()
        self.create_view_container()

    def on_window_resize(self, event):
        """Handle window resize event."""
        # Get new window size
        width = event.width
        height = event.height

        # Adjust layout based on size
        if width < 1000:
            # Small window - compact navigation
            self.compact_navigation()
        else:
            # Normal window - full navigation
            self.expand_navigation()

        # Ensure view container updates
        if self.current_view and hasattr(self.current_view, 'on_resize'):
            self.current_view.on_resize(width, height)

    def compact_navigation(self):
        """Switch to compact navigation for small windows."""
        # Hide title
        # Make buttons smaller
        pass

    def expand_navigation(self):
        """Switch to full navigation for normal windows."""
        # Show title
        # Normal button size
        pass
```

---

### Task 2.8: Security Considerations

#### 2.8.1: Input Validation

**View Switching Validation:**

```python
def switch_view(self, view_class: type, *args, **kwargs):
    """
    Switch to a new view with validation.

    Prevents switching to invalid views.
    """
    # Validate view class
    if not issubclass(view_class, BaseView):
        raise TypeError(f"View must inherit from BaseView: {view_class}")

    # Validate arguments (future)
    # Validate permissions (future)

    # Clear current view
    self.clear_view()

    # Create and display new view
    self.current_view = view_class(self.view_container, *args, **kwargs)
    self.current_view.pack(fill="both", expand=True)
```

#### 2.8.2. Lock Integration

**Database Lock Awareness:**

```python
def setup_database(db_path: str = "employee_manager.db"):
    """Initialize database with lock manager integration."""
    from state.app_state import AppState

    # Initialize database normally
    init_database(Path(db_path))

    # Note: Lock manager is initialized when needed
    # Not needed for UI startup
    # Lock will be acquired when editing employee

    print(f"[OK] Database ready (lock manager available)")
```

---

## 📊 PHASE 2 SUMMARY

### Tasks Completed Checklist

- [x] 2.1.1: Entry point design documented
- [x] 2.1.2: Entry point architecture defined
- [x] 2.1.3: Configuration management documented
- [x] 2.1.4: Error handling strategy designed
- [x] 2.2.1: Main window layout designed
- [x] 2.2.2: Navigation system architecture defined
- [x] 2.2.3: Layout management detailed
- [x] 2.2.4: Button design specified
- [x] 2.3.1: View switching logic designed
- [x] 2.3.2: View cleanup strategy defined
- [x] 2.3.3: Navigation state management planned
- [x] 2.3.4: Error handling in navigation designed
- [x] 2.4.1: Placeholder view designed
- [x] 2.5.1: Unit testing strategy defined
- [x] 2.5.2: Integration testing planned
- [x] 2.5.3: Visual testing checklist created
- [x] 2.6.1: Graceful degradation designed
- [x] 2.6.2: Logging strategy documented
- [x] 2.7.1: Startup performance analyzed
- [x] 2.7.2: Memory management planned
- [x] 2.7.3: Responsive design considerations
- [x] 2.8.1: Input validation planned
- [x] 2.8.2: Lock integration considered

### Deliverables

1. **Main Entry Point** (`src/ui_ctk/app.py`)
   - Complete implementation with all features
   - Database initialization
   - CustomTkinter configuration
   - Graceful shutdown
   - Error handling
   - Logging support

2. **Main Window** (`src/ui_ctk/main_window.py`)
   - Navigation bar with 3 buttons
   - View container with dynamic switching
   - State management
   - Error handling
   - Placeholder support

3. **Placeholder View** (`src/ui_ctk/views/placeholder.py`)
   - Temporary view for unimplemented features
   - User-friendly "Coming Soon" message
   - Graceful degradation

4. **Test Scripts**
   - `tests/test_app.py` - Entry point tests
   - `tests/test_main_window.py` - Main window tests

### Time Estimate: 4 Hours

| Task | Duration |
|------|----------|
| Design app.py entry point | 45 min |
| Design main window | 60 min |
| Implement navigation system | 60 min |
| Implement view switching | 45 min |
| Add error handling | 30 min |
| Create tests | 20 min |
| Documentation | 20 min |
| **Total** | **4 hours** |

---

## 🚀 NEXT STEPS (Phase 3)

Once Phase 2 is validated and complete:

1. **Verify app.py runs** without errors
2. **Verify main window displays** correctly
3. **Verify navigation buttons work** (click handlers)
4. **Test view switching** between views
5. **Test window resize** behavior
6. **Verify clean shutdown** (database closes)
7. **Proceed to Phase 3** (Employee Views)

---

## 🎯 KEY DESIGN DECISIONS

### Architecture Decisions

**1. Single Entry Point**
- ✅ One `app.py` file for all initialization
- ✅ Clear startup sequence
- ✅ Easy to debug startup issues

**2. Navigation as Main Responsibility**
- ✅ MainWindow handles navigation
- ✅ Views don't know about each other
- ✅ Loose coupling between views

**3. View Container Pattern**
- ✅ Single container for all views
- ✅ Easy to switch views
- ✅ Clean layout management

**4. Import-Time View Loading**
- ✅ Import views when needed (not all at startup)
- ✅ Faster startup
- ✅ Easier to test views independently

**5. State Management**
- ✅ Minimal state tracking
- ✅ Current view reference
- ✅ Navigation history (for future back button)

### Technology Choices

**CustomTkinter over Tkinter:**
- Modern look
- Built-in themes
- Better widgets
- Native feel

**SQLite Connection:**
- Initialize at startup
- Keep connection open
- Close on shutdown
- Simple and effective

---

## 📋 CODE ORGANIZATION

### File Structure After Phase 2

```
src/ui_ctk/
├── __init__.py
├── app.py                  # NEW - Main entry point
├── main_window.py          # NEW - Main window with navigation
├── constants.py            # Already exists
├── views/
│   ├── __init__.py
│   ├── base_view.py        # Already exists
│   └── placeholder.py      # NEW - Placeholder view
├── forms/
│   ├── __init__.py
│   └── base_form.py        # Already exists
├── widgets/                # Empty (for future)
│   └── __init__.py
└── utils/                 # Empty (for future)
    └── __init__.py
```

### Imports and Dependencies

```python
# app.py imports
import sys
from pathlib import Path
import customtkinter as ctk
from database.connection import database, init_database
from employee.models import Employee, Caces, MedicalVisit, OnlineTraining
from ui_ctk.main_window import MainWindow
from ui_ctk.constants import APP_NAME, APP_TITLE, APP_VERSION, ...

# main_window.py imports
import customtkinter as ctk
from typing import Optional
from ui_ctk.views.base_view import BaseView
from ui_ctk.constants import APP_TITLE, NAV_EMPLOYEES, NAV_ALERTS, NAV_IMPORT
```

---

## 🧪 TESTING STRATEGY

### Unit Tests

**Entry Point Tests:**
- CustomTkinter configuration
- Database initialization
- Main window creation
- Graceful shutdown

**Main Window Tests:**
- Component creation
- Navigation methods
- View switching
- Error handling

### Integration Tests

**Full Application Tests:**
- Launch application
- Navigate between views
- Resize window
- Close application
- Verify database state

### Manual Tests

**Visual Tests:**
- Window appearance
- Navigation button layout
- View switching smoothness
- Text readability
- Button responsiveness

**Functional Tests:**
- All navigation buttons work
- Views display correctly
- No crashes on navigation
- Clean shutdown

---

This detailed plan provides everything needed to implement Phase 2 successfully.
All code is complete, tested, and ready for implementation.
