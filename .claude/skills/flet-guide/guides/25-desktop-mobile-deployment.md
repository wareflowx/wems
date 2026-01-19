# Desktop and Mobile Deployment

Package your Flet applications for Windows, macOS, Linux, iOS, and Android.

## Desktop Deployment

### Windows Executable

```bash
# Build Windows executable
flet build windows

# Output: dist/your-app.exe
```

### macOS Application

```bash
# Build macOS app
flet build macos

# Output: dist/your-app.app
```

### Linux Package

```bash
# Build Linux package
flet build linux

# Output: dist/your-app
```

### Desktop Build Options

```bash
# Custom icon
flet build windows --icon app-icon.ico

# Custom product name
flet build macos --product "My App"

# Add file associations
flet build windows --add-file-extension ".txt"
```

## Mobile Deployment

### Android APK

```bash
# Build Android APK
flet build apk

# Output: build/app/outputs/flutter-apk/app-release.apk
```

### Android App Bundle

```bash
# Build AAB for Play Store
flet build aab

# Output: build/app/outputs/bundle/release/app-release.aab
```

### iOS IPA

```bash
# Build iOS app
flet build ipa

# Requires macOS and Xcode
# Output: build/ios/archive/Runner.xcarchive
```

### Mobile Configuration

```python
import flet as ft

def main(page: ft.Page):
    # Mobile-specific settings
    page.appbar = ft.AppBar(
        title="My App",
        bgcolor=ft.Colors.BLUE,
    )

    # Handle mobile back button
    def on_view_pop(view):
        page.go("/")

    page.on_view_pop = on_view_pop

    page.add(ft.Text("Mobile App"))

ft.run(main)
```

## Build Configuration

### pyproject.toml

```toml
[project]
name = "my-app"
version = "1.0.0"

[tool.flet]
app_name = "My App"
product = "My App"
company = "My Company"
copyright = "Copyright 2025"
description = "My Flet Application"

[tool.flet.android]
package_name = "com.example.myapp"
min_sdk_version = 21

[tool.flet.ios]
bundle_id = "com.example.myapp"
```

## Best Practices

### 1. Test Before Building

```bash
# Test on target platform first
flet run --device android
```

### 2. Use Appropriate Build

```python
# Platform-specific code
if page.platform:
    # Mobile
    layout = ft.MobileLayout()
else:
    # Desktop
    layout = ft.DesktopLayout()
```

### 3. Handle Screen Sizes

```python
def handle_resize(e):
    if page.window_width < 600:
        # Mobile layout
        pass
    else:
        # Desktop layout
        pass

page.on_resize = handle_resize
```

## Next Steps

1. Publish web apps
2. Test thoroughly
3. Deploy to production
4. Monitor usage
