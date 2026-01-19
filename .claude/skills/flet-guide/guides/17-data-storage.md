# Data Storage and Persistence

Flet provides multiple options for storing data on the client side, from simple key-value storage to file system access.

## Client Storage

### Store Client Data

```python
import flet as ft

def main(page: ft.Page):
    # Get client storage instance
    storage = page.client_storage

    # Save data
    storage.set("username", "john_doe")
    storage.set("theme", "dark")

    # Retrieve data
    username = storage.get("username")
    theme = storage.get("theme")

    page.add(
        ft.Text(f"Username: {username}"),
        ft.Text(f"Theme: {theme}")
    )

ft.run(main)
```

### Check Key Exists

```python
def main(page: ft.Page):
    storage = page.client_storage

    def save_preferences(e):
        storage.set("dark_mode", dark_mode.value)
        page.snack_bar = ft.SnackBar(ft.Text("Preferences saved!"))
        page.snack_bar.open = True
        page.update()

    dark_mode = ft.Switch(label="Dark Mode")
    dark_mode.value = storage.get("dark_mode", False)

    page.add(
        dark_mode,
        ft.Button("Save", on_click=save_preferences)
    )

ft.run(main)
```

## Session Storage

### Session-Based Storage

```python
def main(page: ft.Page):
    # Session data is cleared when app closes
    page.session.set("temp_data", "temporary")

    def handle_action(e):
        temp = page.session.get("temp_data")
        print(f"Session data: {temp}")

    page.add(
        ft.Button("Get Session Data", on_click=handle_action)
    )

ft.run(main)
```

## SharedPreferences

### Platform-Specific Storage

```python
def main(page: ft.Page):
    # Access SharedPreferences service
    prefs = page.shared_preferences

    # Note: In newer Flet versions, use client_storage instead
    # This is maintained for compatibility

    page.add(
        ft.Text("Use client_storage instead of shared_preferences")
    )

ft.run(main)
```

## File System Access

### Read Files

```python
def main(page: ft.Page):
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)

    content = ft.TextField(label="File Content", multiline=True, min_lines=10)

    def handle_file_select(e):
        if e.files:
            try:
                with open(e.files[0].path, 'r') as f:
                    content.value = f.read()
                    page.update()
            except Exception as ex:
                content.value = f"Error: {ex}"
                page.update()

    file_picker.on_result = handle_file_select

    page.add(
        content,
        ft.ElevatedButton("Open File", on_click=lambda _: file_picker.pick_files())
    )

ft.run(main)
```

### Write Files

```python
def main(page: ft.Page):
    save_picker = ft.FilePicker()
    page.overlay.append(save_picker)

    text_area = ft.TextField(label="Content", multiline=True, min_lines=10)

    def handle_save(e):
        save_picker.save_file(
            dialog_title="Save File",
            file_type=ft.FilePickerFileType.ANY
        )

    def handle_save_result(e):
        if e.path:
            try:
                with open(e.path, 'w') as f:
                    f.write(text_area.value)
                page.snack_bar = ft.SnackBar(ft.Text("File saved!"))
                page.snack_bar.open = True
                page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"))
                page.snack_bar.open = True
                page.update()

    save_picker.on_result = handle_save_result

    page.add(
        text_area,
        ft.ElevatedButton("Save", on_click=handle_save)
    )

ft.run(main)
```

## Download Directory

### Get Download Path

```python
def main(page: ft.Page):
    def get_download_path(e):
        try:
            paths = page.storage_paths.get_downloads_path()
            page.snack_bar = ft.SnackBar(ft.Text(f"Downloads: {paths}"))
            page.snack_bar.open = True
            page.update()
        except Exception as ex:
            print(f"Error: {ex}")

    page.add(
        ft.Button("Get Downloads Path", on_click=get_download_path)
    )

ft.run(main)
```

## Data Persistence Patterns

### User Preferences

```python
class UserPreferences:
    def __init__(self, page):
        self.page = page
        self.storage = page.client_storage

    def load(self):
        return {
            "theme": self.storage.get("theme", "light"),
            "language": self.storage.get("language", "en"),
            "notifications": self.storage.get("notifications", True),
        }

    def save(self, prefs):
        self.storage.set("theme", prefs["theme"])
        self.storage.set("language", prefs["language"])
        self.storage.set("notifications", prefs["notifications"])

def main(page: ft.Page):
    prefs = UserPreferences(page)
    user_prefs = prefs.load()

    theme_switch = ft.Switch(label="Dark Mode", value=user_prefs["theme"] == "dark")

    def save_settings(e):
        new_prefs = {
            "theme": "dark" if theme_switch.value else "light",
            "language": "en",
            "notifications": True,
        }
        prefs.save(new_prefs)
        page.snack_bar = ft.SnackBar(ft.Text("Settings saved!"))
        page.snack_bar.open = True
        page.update()

    page.add(
        theme_switch,
        ft.Button("Save Settings", on_click=save_settings)
    )

ft.run(main)
```

### Remember Me Pattern

```python
def main(page: ft.Page):
    username = ft.TextField(label="Username")
    password = ft.TextField(label="Password", password=True)
    remember = ft.Checkbox(label="Remember me")

    # Load saved credentials
    if page.client_storage.get("remember"):
        username.value = page.client_storage.get("username", "")
        password.value = page.client_storage.get("password", "")
        remember.value = True

    def handle_login(e):
        if remember.value:
            page.client_storage.set("username", username.value)
            page.client_storage.set("password", password.value)
            page.client_storage.set("remember", True)
        else:
            page.client_storage.clear()
            page.client_storage.set("remember", False)

        print(f"Login: {username.value}")

    page.add(
        username,
        password,
        remember,
        ft.Button("Login", on_click=handle_login)
    )

ft.run(main)
```

## Best Practices

### 1. Use Appropriate Storage

```python
# Good - Use client_storage for small data
page.client_storage.set("preference", "value")

# Use files for larger data
with open("data.json", "w") as f:
    json.dump(data, f)
```

### 2. Handle Missing Data

```python
# Good - Provide defaults
username = storage.get("username", "guest")

# Avoid - Assume data exists
username = storage.get("username")  # Might be None
```

### 3. Clear Sensitive Data

```python
def logout(e):
    # Clear sensitive data
    storage.remove("password")
    storage.remove("token")
```

## Next Steps

With data storage covered:

1. Implement authentication
2. Work with system services
3. Add geolocation
4. Handle media files
5. Draw on canvas
