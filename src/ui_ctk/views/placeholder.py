"""Placeholder view for unimplemented screens."""

import customtkinter as ctk

from ui_ctk.views.base_view import BaseView


class PlaceholderView(BaseView):
    """Placeholder view for unimplemented features."""

    def __init__(self, master, title: str = "Coming Soon"):
        super().__init__(master, title=title)

        # Create placeholder content
        label = ctk.CTkLabel(self, text=f"{title}\n\nComing Soon", font=("Arial", 24))
        label.pack(expand=True)

        info_label = ctk.CTkLabel(
            self, text="This feature will be implemented in a future update.", font=("Arial", 14), text_color="gray"
        )
        info_label.pack(pady=20)
