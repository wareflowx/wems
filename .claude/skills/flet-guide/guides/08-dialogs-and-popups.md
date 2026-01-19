# Dialogs and Popups

Dialogs and popups are essential for displaying important information, gathering user input, and confirming actions. This guide covers all modal and overlay components in Flet.

## AlertDialog

Simple alert dialogs for messages and confirmations.

### Basic Alert

```python
import flet as ft

def main(page: ft.Page):
    def show_alert(e):
        page.dialog = ft.AlertDialog(
            title=ft.Text("Alert"),
            content=ft.Text("This is an alert message"),
            actions=[
                ft.TextButton("OK", on_click=lambda e: close_dialog()),
            ],
        )
        page.dialog.open = True
        page.update()

    def close_dialog():
        page.dialog.open = False
        page.update()

    page.add(
        ft.ElevatedButton("Show Alert", on_click=show_alert)
    )

ft.run(main)
```

### Confirmation Dialog

```python
def main(page: ft.Page):
    def show_confirmation(e):
        def confirm(e):
            print("Confirmed!")
            close_dialog()

        def cancel(e):
            print("Cancelled")
            close_dialog()

        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Action"),
            content=ft.Text("Are you sure you want to proceed?"),
            actions=[
                ft.TextButton("Cancel", on_click=cancel),
                ft.TextButton("Confirm", on_click=confirm),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog.open = True
        page.update()

    def close_dialog():
        page.dialog.open = False
        page.update()

    page.add(
        ft.ElevatedButton("Delete Item", on_click=show_confirmation,
                         bgcolor=ft.Colors.RED, color=ft.Colors.WHITE)
    )

ft.run(main)
```

### Alert with Icon

```python
def main(page: ft.Page):
    def show_alert(e):
        page.dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.WARNING, color=ft.Colors.ORANGE),
                ft.Text("Warning", color=ft.Colors.ORANGE),
            ], spacing=10),
            content=ft.Text("This action cannot be undone"),
            bgcolor=ft.Colors.ORANGE_50,
            actions=[
                ft.TextButton("I Understand", on_click=lambda e: close_dialog()),
            ],
        )
        page.dialog.open = True
        page.update()

    def close_dialog():
        page.dialog.open = False
        page.update()

    page.add(
        ft.ElevatedButton("Show Warning", on_click=show_alert)
    )

ft.run(main)
```

## BottomSheet

Modal bottom sheet that slides up from the bottom of the screen.

### Simple BottomSheet

```python
def main(page: ft.Page):
    def show_bottom_sheet(e):
        page.bottom_sheet = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Bottom Sheet", size=24, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=20),
                    ft.Text("Content goes here"),
                    ft.Divider(height=20),
                    ft.ElevatedButton("Close", on_click=close_bottom_sheet),
                ], tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
            ),
            bgcolor=ft.Colors.WHITE,
            elevation=10,
        )
        page.bottom_sheet.open = True
        page.update()

    def close_bottom_sheet(e):
        page.bottom_sheet.open = False
        page.update()

    page.add(
        ft.ElevatedButton("Show Bottom Sheet", on_click=show_bottom_sheet)
    )

ft.run(main)
```

### BottomSheet with List

```python
def main(page: ft.Page):
    def show_sheet(e):
        page.bottom_sheet = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column([
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.SHARE),
                        title=ft.Text("Share"),
                        on_click=lambda e: handle_action("Share"),
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.LINK),
                        title=ft.Text("Get Link"),
                        on_click=lambda e: handle_action("Get Link"),
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.EDIT),
                        title=ft.Text("Edit"),
                        on_click=lambda e: handle_action("Edit"),
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.DELETE),
                        title=ft.Text("Delete", color=ft.Colors.RED),
                        on_click=lambda e: handle_action("Delete"),
                    ),
                ], tight=True),
                padding=10,
            ),
        )
        page.bottom_sheet.open = True
        page.update()

    def handle_action(action):
        print(f"Action: {action}")
        page.bottom_sheet.open = False
        page.update()

    page.add(
        ft.ElevatedButton("Show Options", on_click=show_sheet)
    )

ft.run(main)
```

## Snackbar

Temporary message displayed at the bottom of the screen.

### Basic Snackbar

```python
def main(page: ft.Page):
    def show_snackbar(e):
        page.snack_bar = ft.SnackBar(
            ft.Text("Message sent successfully!")
        )
        page.snack_bar.open = True
        page.update()

    page.add(
        ft.ElevatedButton("Show Snackbar", on_click=show_snackbar)
    )

ft.run(main)
```

### Snackbar with Action

```python
def main(page: ft.Page):
    def show_snackbar(e):
        def handle_action(e):
            print("Undo clicked")

        page.snack_bar = ft.SnackBar(
            content=ft.Text("Item deleted"),
            action=ft.TextButton("UNDO", on_click=handle_action),
            duration=5000,  # 5 seconds
            bgcolor=ft.Colors.BLUE,
        )
        page.snack_bar.open = True
        page.update()

    page.add(
        ft.ElevatedButton("Delete Item", on_click=show_snackbar)
    )

ft.run(main)
```

### Success/Error Snackbars

```python
def main(page: ft.Page):
    def show_success(e):
        page.snack_bar = ft.SnackBar(
            ft.Text("Operation completed successfully!"),
            bgcolor=ft.Colors.GREEN,
        )
        page.snack_bar.open = True
        page.update()

    def show_error(e):
        page.snack_bar = ft.SnackBar(
            ft.Text("An error occurred!"),
            bgcolor=ft.Colors.RED,
        )
        page.snack_bar.open = True
        page.update()

    page.add(
        ft.Row([
            ft.ElevatedButton("Success", on_click=show_success,
                             bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE),
            ft.ElevatedButton("Error", on_click=show_error,
                             bgcolor=ft.Colors.RED, color=ft.Colors.WHITE),
        ], spacing=10)
    )

ft.run(main)
```

## DatePicker

Date selection dialog.

```python
def main(page: ft.Page):
    def handle_date_change(e):
        date_picker.value = e.control.value
        date_text.value = f"Selected: {date_picker.value}"
        page.update()

    date_picker = ft.DatePicker(
        on_change=handle_date_change,
        first_date=datetime(2023, 1, 1),
        last_date=datetime(2025, 12, 31),
    )

    date_text = ft.Text("No date selected")

    def show_date_picker(e):
        page.open(date_picker)

    page.add(
        ft.Column([
            date_text,
            ft.ElevatedButton("Pick Date", on_click=show_date_picker),
        ])
    )

ft.run(main)
```

## TimePicker

Time selection dialog.

```python
def main(page: ft.Page):
    def handle_time_change(e):
        time_text.value = f"Selected: {time_picker.value}"
        page.update()

    time_picker = ft.TimePicker(
        on_change=handle_time_change,
    )

    time_text = ft.Text("No time selected")

    def show_time_picker(e):
        page.open(time_picker)

    page.add(
        ft.Column([
            time_text,
            ft.ElevatedButton("Pick Time", on_click=show_time_picker),
        ])
    )

ft.run(main)
```

## Menu and PopupMenuButton

Dropdown menus for additional options.

### PopupMenuButton

```python
def main(page: ft.Page):
    def handle_menu_item(e):
        print(f"Selected: {e.control.text}")

    page.add(
        ft.PopupMenuButton(
            items=[
                ft.PopupMenuItem(text="Option 1", on_click=handle_menu_item),
                ft.PopupMenuItem(text="Option 2", on_click=handle_menu_item),
                ft.PopupMenuItem(icon=ft.Icons.REFRESH, text="Refresh"),
                ft.PopupMenuItem(),  # Divider
                ft.PopupMenuItem(text="Settings", icon=ft.Icons.SETTINGS),
            ],
        )
    )

ft.run(main)
```

### Custom Menu with MenuBar

```python
def main(page: ft.Page):
    page.appbar = ft.AppBar(
        title=ft.Text("Menu Bar Example"),
        actions=[
            ft.MenuBar(
                style=ft.ButtonStyle(bgcolor={ft.MaterialState.HOVERED: ft.Colors.with_opacity(0.5, ft.Colors.GREY)}),
                controls=[
                    ft.SubmenuButton(
                        content=ft.Text("File"),
                        controls=[
                            ft.MenuItemButton(content=ft.Text("New"), on_click=lambda e: print("New")),
                            ft.MenuItemButton(content=ft.Text("Open"), on_click=lambda e: print("Open")),
                            ft.MenuItemButton(content=ft.Text("Save"), on_click=lambda e: print("Save")),
                        ]
                    ),
                    ft.SubmenuButton(
                        content=ft.Text("Edit"),
                        controls=[
                            ft.MenuItemButton(content=ft.Text("Cut"), on_click=lambda e: print("Cut")),
                            ft.MenuItemButton(content=ft.Text("Copy"), on_click=lambda e: print("Copy")),
                            ft.MenuItemButton(content=ft.Text("Paste"), on_click=lambda e: print("Paste")),
                        ]
                    ),
                ]
            )
        ]
    )

    page.add(ft.Text("Menu Bar Example"))

ft.run(main)
```

## Banner

Important announcement banner at the top of content.

```python
def main(page: ft.Page):
    def handle_dismiss(e):
        banner.visible = False
        page.update()

    def handle_action(e):
        print("Learn more clicked")

    banner = ft.Banner(
        bgcolor=ft.Colors.AMBER_100,
        leading=ft.Icon(ft.Icons.WARNING, color=ft.Colors.AMBER, size=40),
        content=ft.Text("Important announcement: Update your app to the latest version"),
        actions=[
            ft.TextButton("Learn More", on_click=handle_action),
            ft.TextButton("Dismiss", on_click=handle_dismiss),
        ],
    )

    page.add(
        ft.Column([
            banner,
            ft.Text("Content here"),
        ])
    )

ft.run(main)
```

## Modal Overlay

Custom modal overlay with semi-transparent background.

```python
def main(page: ft.Page):
    def show_modal(e):
        modal = ft.Stack([
            # Semi-transparent background
            ft.Container(
                bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
                width=page.window_width,
                height=page.window_height,
            ),
            # Modal content
            ft.Container(
                content=ft.Column([
                    ft.Text("Custom Modal", size=24, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=20),
                    ft.Text("This is a custom modal overlay"),
                    ft.Divider(height=20),
                    ft.Row([
                        ft.ElevatedButton("Close", on_click=lambda e: close_modal(modal)),
                    ], alignment=ft.MainAxisAlignment.END),
                ], tight=True),
                bgcolor=ft.Colors.WHITE,
                padding=30,
                border_radius=10,
                width=400,
                left=page.window_width / 2 - 200,
                top=page.window_height / 2 - 150,
            ),
        ], width=page.window_width, height=page.window_height)

        page.add(modal)
        page.update()

    def close_modal(modal):
        page.remove(modal)
        page.update()

    page.add(
        ft.ElevatedButton("Show Modal", on_click=show_modal)
    )

ft.run(main)
```

## Form Dialog

Dialog with form inputs.

```python
def main(page: ft.Page):
    name_field = ft.TextField(label="Name")
    email_field = ft.TextField(label="Email")

    def show_form_dialog(e):
        def submit(e):
            print(f"Name: {name_field.value}, Email: {email_field.value}")
            close_dialog()

        def cancel(e):
            close_dialog()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Add User"),
            content=ft.Column([
                name_field,
                email_field,
            ], tight=True, width=300),
            actions=[
                ft.TextButton("Cancel", on_click=cancel),
                ft.ElevatedButton("Submit", on_click=submit),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog.open = True
        page.update()

    def close_dialog():
        page.dialog.open = False
        page.update()

    page.add(
        ft.ElevatedButton("Add User", on_click=show_form_dialog)
    )

ft.run(main)
```

## Progress Dialog

Dialog showing loading progress.

```python
import time

def main(page: ft.Page):
    def show_progress_dialog(e):
        progress_text = ft.Text("Processing...", size=16)
        progress_bar = ft.ProgressBar(width=300)

        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Please Wait"),
            content=ft.Column([
                progress_bar,
                progress_text,
            ], tight=True, width=300, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        )
        page.dialog.open = True
        page.update()

        # Simulate progress
        for i in range(1, 101):
            time.sleep(0.03)
            progress_bar.value = i / 100
            progress_text.value = f"Processing... {i}%"
            page.update()

        # Close dialog
        page.dialog.open = False
        page.update()

        # Show success
        page.snack_bar = ft.SnackBar(
            ft.Text("Operation completed!"),
            bgcolor=ft.Colors.GREEN,
        )
        page.snack_bar.open = True
        page.update()

    page.add(
        ft.ElevatedButton("Start Process", on_click=show_progress_dialog)
    )

ft.run(main)
```

## Common Patterns

### Confirm Before Destructive Action

```python
def main(page: ft.Page):
    def handle_delete(e):
        def confirm(e):
            print("Item deleted")
            close_dialog()

        def cancel(e):
            close_dialog()

        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.WARNING, color=ft.Colors.RED, size=30),
                ft.Text("Delete Item", color=ft.Colors.RED),
            ], spacing=10),
            content=ft.Text("This action cannot be undone. Are you sure?"),
            actions=[
                ft.TextButton("Cancel", on_click=cancel),
                ft.ElevatedButton(
                    "Delete",
                    on_click=confirm,
                    bgcolor=ft.Colors.RED,
                    color=ft.Colors.WHITE,
                ),
            ],
        )
        page.dialog.open = True
        page.update()

    def close_dialog():
        page.dialog.open = False
        page.update()

    page.add(
        ft.ElevatedButton(
            "Delete Item",
            on_click=handle_delete,
            bgcolor=ft.Colors.RED,
            color=ft.Colors.WHITE,
        )
    )

ft.run(main)
```

### Success Feedback

```python
def main(page: ft.Page):
    def handle_action(e):
        # Perform action
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Action completed successfully!"),
            bgcolor=ft.Colors.GREEN,
            duration=3000,
        )
        page.snack_bar.open = True
        page.update()

    page.add(
        ft.ElevatedButton("Perform Action", on_click=handle_action)
    )

ft.run(main)
```

### Loading Overlay

```python
def main(page: ft.Page):
    loading_overlay = ft.Container(
        visible=False,
        content=ft.Stack([
            ft.Container(
                bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
                width=page.window_width,
                height=page.window_height,
            ),
            ft.Container(
                content=ft.Column([
                    ft.ProgressRing(color=ft.Colors.WHITE),
                    ft.Text("Loading...", color=ft.Colors.WHITE, size=16),
                ], tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.BLACK),
                padding=30,
                border_radius=10,
            ),
        ], width=page.window_width, height=page.window_height)
    )

    def start_loading(e):
        loading_overlay.visible = True
        page.update()

        # Simulate loading
        import time
        time.sleep(2)

        loading_overlay.visible = False
        page.update()

    page.add(
        ft.Column([
            ft.ElevatedButton("Start Loading", on_click=start_loading),
            ft.Text("Content here"),
        ])
    )

ft.run(main)
```

## Best Practices

### 1. Use Appropriate Dialog Type

- Use `AlertDialog` for simple messages and confirmations
- Use `BottomSheet` for lists of options
- Use `SnackBar` for temporary feedback
- Use `DatePicker`/`TimePicker` for date/time selection

### 2. Always Provide Close Options

```python
# Good - User can dismiss
ft.AlertDialog(
    content=ft.Text("Message"),
    actions=[ft.TextButton("OK", on_click=close)],
)
```

### 3. Use Modals for Important Actions

```python
# Good - Modal prevents interaction
ft.AlertDialog(modal=True, ...)
```

### 4. Provide Context in Messages

```python
# Good - Specific message
ft.Text("File 'report.pdf' deleted successfully")

# Avoid - Generic message
ft.Text("Success")
```

### 5. Use Icons to Convey Meaning

```python
# Good - Icon + text
ft.Row([
    ft.Icon(ft.Icons.WARNING, color=ft.Colors.RED),
    ft.Text("Error occurred")
])
```

### 6. Set Appropriate Durations

```python
# Good - Readable duration
ft.SnackBar(duration=3000)  # 3 seconds

# Avoid - Too short
ft.SnackBar(duration=500)  # 0.5 seconds
```

## Next Steps

With dialogs and popups covered:

1. Learn about navigation and routing
2. Master state management
3. Implement event handling patterns
4. Build complete multi-screen applications
5. Add animations and transitions
