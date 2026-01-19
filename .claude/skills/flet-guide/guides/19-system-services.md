# System Services

Flet provides access to various platform services for interacting with device capabilities.

## Clipboard

### Copy and Paste

```python
import flet as ft

def main(page: ft.Page):
    clipboard = page.clipboard

    text_field = ft.TextField(label="Text to copy")
    display = ft.TextField(label="Clipboard content", read_only=True)

    def copy_to_clipboard(e):
        clipboard.set_text(text_field.value)
        page.snack_bar = ft.SnackBar(ft.Text("Copied!"))
        page.snack_bar.open = True
        page.update()

    def get_from_clipboard(e):
        display.value = clipboard.get_text()
        page.update()

    page.add(
        text_field,
        ft.Button("Copy", on_click=copy_to_clipboard),
        ft.Divider(),
        display,
        ft.Button("Paste", on_click=get_from_clipboard)
    )

ft.run(main)
```

## File Picker

### Select Files

```python
def main(page: ft.Page):
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)

    selected_files = ft.Text("No files selected")

    def handle_pick(e):
        if e.files:
            names = ", ".join([f.name for f in e.files])
            selected_files.value = names
            page.update()

    file_picker.on_result = handle_pick

    page.add(
        selected_files,
        ft.ElevatedButton(
            "Select Files",
            on_click=lambda _: file_picker.pick_files()
        )
    )

ft.run(main)
```

## Share Service

### Share Content

```python
def main(page: ft.Page):
    share = page.share

    def share_text(e):
        share.share_text("Check out this app!")

    def share_file(e):
        share.share_files(["path/to/file.pdf"])

    page.add(
        ft.Button("Share Text", on_click=share_text),
        ft.Button("Share File", on_click=share_file)
    )

ft.run(main)
```

## Connectivity

### Check Network Status

```python
def main(page: ft.Page):
    connectivity = page.connectivity

    def check_connection(e):
        is_connected = connectivity.is_connected()
        status.value = f"Connected: {is_connected}"
        page.update()

    status = ft.Text("Unknown")

    page.add(
        status,
        ft.Button("Check Connection", on_click=check_connection)
    )

ft.run(main)
```

## Best Practices

### 1. Handle Permissions

```python
# Check permissions before accessing services
if page.client_storage:
    # Use storage
    pass
```

### 2. Provide Fallbacks

```python
# Good - Fallback
try:
    clipboard = page.clipboard
    clipboard.set_text(text)
except:
    # Fallback behavior
    pass
```

## Next Steps

1. Add geolocation
2. Work with media
3. Draw on canvas
4. Build complete apps
5. Deploy applications
