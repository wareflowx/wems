"""Login view for user authentication.

This module provides a secure login interface with:
- Username/password authentication
- Error handling and user feedback
- Session management
- Automatic login on success
"""

import customtkinter as ctk
from typing import Optional, Callable

from auth.authentication import (
    AuthenticationService,
    AuthenticationError,
    AccountLockedError,
    InvalidCredentialsError,
)
from auth.models import create_tables, User, Role
from auth.session import SessionManager, login as create_session
from ui_ctk.constants import (
    BTN_LOGIN,
    BTN_CANCEL,
    APP_TITLE,
)


class LoginView(ctk.CTkFrame):
    """
    Login view for user authentication.

    Features:
    - Secure username/password entry
    - Real-time validation feedback
    - Error message display
    - Account lockout warnings
    - Session creation on success
    - Callback for successful login
    """

    def __init__(self, master, login_success_callback: Optional[Callable] = None):
        """
        Initialize login view.

        Args:
            master: Parent window
            login_success_callback: Function to call on successful login
        """
        super().__init__(master, fg_color="transparent")

        self.login_success_callback = login_success_callback
        self.auth_service = AuthenticationService()
        self.session_manager = SessionManager()

        # Form variables
        self.username_var = ctk.StringVar()
        self.password_var = ctk.StringVar()

        # Create UI
        self.create_login_form()

        # Focus on username field
        self.username_entry.focus_set()

        # Ensure User table exists
        try:
            create_tables()
        except Exception as e:
            print(f"[WARN] Failed to create auth tables: {e}")

    def create_login_form(self):
        """Create login form UI."""
        # Center container
        login_container = ctk.CTkFrame(self, width=400, height=450)
        login_container.place(relx=0.5, rely=0.5, anchor="center")

        # App title
        title_label = ctk.CTkLabel(
            login_container,
            text=APP_TITLE,
            font=("Arial", 28, "bold"),
            text_color=("#1f5f8b", "#dce4ee")
        )
        title_label.pack(pady=(40, 10))

        # Subtitle
        subtitle_label = ctk.CTkLabel(
            login_container,
            text="Employee Management System",
            font=("Arial", 14),
            text_color="gray"
        )
        subtitle_label.pack(pady=(0, 30))

        # Login form
        form_frame = ctk.CTkFrame(login_container, width=350)
        form_frame.pack(padx=20, pady=10)

        # Username field
        username_label = ctk.CTkLabel(
            form_frame,
            text="Username or Email:",
            font=("Arial", 12),
            anchor="w"
        )
        username_label.pack(fill="x", padx=(20, 20), pady=(20, 5))

        self.username_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.username_var,
            placeholder_text="Enter your username",
            width=310,
            height=40
        )
        self.username_entry.pack(padx=(20, 20), pady=(0, 15))

        # Bind Enter key
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())

        # Password field
        password_label = ctk.CTkLabel(
            form_frame,
            text="Password:",
            font=("Arial", 12),
            anchor="w"
        )
        password_label.pack(fill="x", padx=(20, 20), pady=(0, 5))

        self.password_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.password_var,
            placeholder_text="Enter your password",
            show="•",
            width=310,
            height=40
        )
        self.password_entry.pack(padx=(20, 20), pady=(0, 20))

        # Bind Enter key to login
        self.password_entry.bind("<Return>", lambda e: self.on_login())

        # Error message label (hidden by default)
        self.error_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=("Arial", 11),
            text_color="red",
            wraplength=300
        )
        self.error_label.pack(padx=(20, 20), pady=(0, 15))

        # Login button
        self.login_button = ctk.CTkButton(
            form_frame,
            text=BTN_LOGIN,
            command=self.on_login,
            width=310,
            height=40,
            font=("Arial", 14, "bold")
        )
        self.login_button.pack(padx=(20, 20), pady=(0, 10))

        # Cancel button
        cancel_button = ctk.CTkButton(
            form_frame,
            text=BTN_CANCEL,
            command=self.on_cancel,
            width=310,
            height=35,
            fg_color="transparent",
            border_width=2,
            text_color=("#1f5f8b", "#dce4ee")
        )
        cancel_button.pack(padx=(20, 20), pady=(0, 20))

        # Footer info
        footer_label = ctk.CTkLabel(
            login_container,
            text="For authorized use only",
            font=("Arial", 10),
            text_color="gray"
        )
        footer_label.pack(pady=(10, 20))

    def on_login(self):
        """
        Handle login button click.

        Validates credentials and creates session on success.
        """
        username = self.username_var.get().strip()
        password = self.password_var.get()

        # Clear previous error
        self.error_label.configure(text="")

        # Validate input
        if not username:
            self.show_error("Please enter your username or email")
            return

        if not password:
            self.show_error("Please enter your password")
            return

        # Disable login button during authentication
        self.login_button.configure(state="disabled", text="Logging in...")
        self.update()

        try:
            # Attempt authentication
            success, error, user = self.auth_service.authenticate(username, password)

            if success and user:
                # Create session
                create_session(user)

                print(f"[OK] User logged in: {user.username} ({user.role})")

                # Call success callback if provided
                if self.login_success_callback:
                    self.login_success_callback(user)
                else:
                    # Default behavior: close login view
                    self.on_login_success(user)
            else:
                # Show error
                self.show_error(error or "Authentication failed")
                print(f"[AUTH] Login failed: {error}")

                # Clear password for security
                self.password_var.set("")

        except AccountLockedError as e:
            self.show_error(str(e))
            print(f"[AUTH] Account locked: {e}")

        except InvalidCredentialsError as e:
            self.show_error(str(e))
            print(f"[AUTH] Invalid credentials: {e}")

        except AuthenticationError as e:
            self.show_error(f"Authentication error: {e}")
            print(f"[AUTH] Authentication error: {e}")

        except Exception as e:
            self.show_error("An error occurred during login")
            print(f"[ERROR] Login error: {e}")

        finally:
            # Re-enable login button
            self.login_button.configure(state="normal", text=BTN_LOGIN)

    def on_cancel(self):
        """Handle cancel button click."""
        # Clear form
        self.username_var.set("")
        self.password_var.set("")
        self.error_label.configure(text="")

        # Optionally, close application
        # self.master.destroy()

    def on_login_success(self, user: User):
        """
        Handle successful login.

        Args:
            user: Authenticated user
        """
        # Destroy login view
        self.destroy()

        # Show main application
        # Import here to avoid circular import
        from ui_ctk.app import show_main_application

        show_main_application(self.master, user)

    def show_error(self, message: str):
        """
        Display error message to user.

        Args:
            message: Error message to display
        """
        self.error_label.configure(text=message)

    def clear_form(self):
        """Clear login form fields."""
        self.username_var.set("")
        self.password_var.set("")
        self.error_label.configure(text="")


def create_default_admin():
    """
    Create default admin user if no users exist.

    This is a convenience function for initial setup.
    Returns:
        Created admin User or None if users already exist
    """
    try:
        # Check if any users exist
        if User.select().count() > 0:
            return None

        # Create default admin
        admin = User.create_admin(
            username="admin",
            email="admin@wareflow.local",
            password="Admin123!"  # Should be changed on first login
        )

        print(f"[OK] Created default admin user: {admin.username}")
        print("[WARN] Please change the default admin password!")
        return admin

    except Exception as e:
        print(f"[ERROR] Failed to create default admin: {e}")
        return None
