# Theming and Styling

Theming allows you to define consistent visual styles across your entire application. Flet provides a powerful theming system based on Material Design.

## Understanding Themes

A **theme** in Flet defines colors, typography, and component styles for your application.

## App-Wide Theming

### Basic Theme Setup

```python
import flet as ft

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
    )

    page.add(
        ft.Text("Themed Text", size=30),
        ft.ElevatedButton("Themed Button"),
        ft.TextField(label="Themed Field"),
    )

ft.run(main)
```

### Dark Theme

```python
def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
    )

    page.add(
        ft.Text("Dark Mode", size=30),
        ft.ElevatedButton("Dark Button"),
    )

ft.run(main)
```

### System Theme

```python
def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.SYSTEM  # Follows system preference

    page.add(ft.Text("System Theme"))

ft.run(main)
```

## Color Schemes

### Using Material Colors

```python
def main(page: ft.Page):
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.PURPLE,
    )

    page.add(
        ft.Text("Purple Theme", size=30),
        ft.ElevatedButton("Primary Button"),
        ft.OutlinedButton("Outline Button"),
        ft.TextButton("Text Button"),
    )

ft.run(main)
```

### Custom Color Scheme

```python
def main(page: ft.Page):
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE,
            on_primary=ft.Colors.WHITE,
            secondary=ft.Colors.AMBER,
            on_secondary=ft.Colors.BLACK,
            error=ft.Colors.RED,
            on_error=ft.Colors.WHITE,
            background=ft.Colors.WHITE,
            on_background=ft.Colors.BLACK,
            surface=ft.Colors.GREY_100,
            on_surface=ft.Colors.BLACK,
        )
    )

    page.add(ft.Text("Custom Colors"))

ft.run(main)
```

## Typography

### Font Settings

```python
def main(page: ft.Page):
    page.theme = ft.Theme(
        text_theme=ft.TextTheme(
            display_large=ft.TextStyle(
                font_family="Roboto",
                font_size=57,
                weight=ft.FontWeight.W_400,
            ),
            headline_medium=ft.TextStyle(
                font_size=28,
                weight=ft.FontWeight.W_400,
            ),
            body_large=ft.TextStyle(
                font_size=16,
                weight=ft.FontWeight.W_400,
            ),
        )
    )

    page.add(
        ft.Text("Display", style=ft.TextThemeStyle.DISPLAY_LARGE),
        ft.Text("Headline", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
        ft.Text("Body", style=ft.TextThemeStyle.BODY_LARGE),
    )

ft.run(main)
```

## Component Themes

### Button Themes

```python
def main(page: ft.Page):
    page.theme = ft.Theme(
        elevated_button_theme=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE,
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=ft.padding.symmetric(horizontal=20, vertical=15),
        )
    )

    page.add(
        ft.ElevatedButton("Custom Button"),
    )

ft.run(main)
```

### Card Themes

```python
def main(page: ft.Page):
    page.theme = ft.Theme(
        card_theme=ft.CardTheme(
            elevation=5,
            shape=ft.RoundedRectangleBorder(radius=15),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        )
    )

    page.add(
        ft.Card(
            content=ft.Container(
                ft.Text("Themed Card"),
                padding=20,
            )
        )
    )

ft.run(main)
```

### TextField Themes

```python
def main(page: ft.Page):
    page.theme = ft.Theme(
        text_field_theme=ft.TextFieldTheme(
            fill_color=ft.Colors.BLUE_50,
            cursor_color=ft.Colors.BLUE,
            focused_color=ft.Colors.with_opacity(0.1, ft.Colors.BLUE),
        )
    )

    page.add(
        ft.TextField(label="Themed Field"),
    )

ft.run(main)
```

## Local Themes

Override theme for specific controls:

```python
def main(page: ft.Page):
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)

    page.add(
        ft.Column([
            # Uses page theme
            ft.ElevatedButton("Blue Button"),

            # Override with local theme
            ft.Container(
                ft.ElevatedButton("Green Button"),
                theme=ft.Theme(
                    color_scheme_seed=ft.Colors.GREEN,
                ),
            ),
        ])
    )

ft.run(main)
```

## Theme Mode

### Toggle Dark/Light Mode

```python
def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)
    page.dark_theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)

    def toggle_theme(e):
        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.theme_mode = ft.ThemeMode.DARK
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
        page.update()

    theme_switch = ft.Switch(
        label="Dark Mode",
        on_change=toggle_theme
    )

    page.add(
        theme_switch,
        ft.Text("Themeable Content"),
        ft.ElevatedButton("Button"),
    )

ft.run(main)
```

## Custom Fonts

### Load Custom Fonts

```python
def main(page: ft.Page):
    page.fonts = {
        "Roboto": "/fonts/Roboto.ttf",
        "OpenSans": "/fonts/OpenSans.ttf",
    }

    page.theme = ft.Theme(
        text_theme=ft.TextTheme(
            body_large=ft.TextStyle(
                font_family="OpenSans",
                font_size=16,
            ),
        )
    )

    page.add(
        ft.Text("Custom Font Text", font_family="Roboto", size=24),
    )

ft.run(main)
```

## Gradient Backgrounds

```python
def main(page: ft.Page):
    page.bgcolor = ft.Colors.TRANSPARENT
    page.theme = ft.Theme()

    page.add(
        ft.Container(
            ft.Text("Gradient Background", size=30),
            width=page.window_width,
            height=page.window_height,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[
                    ft.Colors.BLUE,
                    ft.Colors.PURPLE,
                    ft.Colors.PINK,
                ]
            ),
            alignment=ft.alignment.center,
        )
    )

ft.run(main)
```

## Responsive Theming

```python
def main(page: ft.Page):
    def handle_resize(e):
        if page.window_width < 600:
            page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)
        else:
            page.theme = ft.Theme(color_scheme_seed=ft.Colors.GREEN)
        page.update()

    page.on_resize = handle_resize

ft.run(main)
```

## Theme Presets

Create reusable theme presets:

```python
THEMES = {
    "blue": ft.Theme(color_scheme_seed=ft.Colors.BLUE),
    "green": ft.Theme(color_scheme_seed=ft.Colors.GREEN),
    "purple": ft.Theme(color_scheme_seed=ft.Colors.PURPLE),
    "red": ft.Theme(color_scheme_seed=ft.Colors.RED),
}

def main(page: ft.Page):
    page.theme = THEMES["blue"]

    def change_theme(e, theme_name):
        page.theme = THEMES[theme_name]
        page.update()

    page.add(
        ft.Row([
            ft.Button(
                name.capitalize(),
                on_click=lambda e, n=name: change_theme(e, n)
            )
            for name in THEMES.keys()
        ])
    )

ft.run(main)
```

## Styled Components

### Styled Card Component

```python
def create_card(title, content, icon=None):
    return ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon) if icon else None,
                    ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
                ], spacing=10) if icon else ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(height=10),
                ft.Text(content),
            ], spacing=10),
            padding=20,
        ),
        elevation=3,
    )

def main(page: ft.Page):
    page.add(
        ft.Column([
            create_card("Card 1", "Content 1", ft.Icons.INFO),
            create_card("Card 2", "Content 2", ft.Icons.WARNING),
        ], spacing=20)
    )

ft.run(main)
```

## Best Practices

### 1. Use Consistent Colors

```python
# Good - Theme-based
page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)

# Avoid - Hardcoded colors
ft.Button("Click", bgcolor="#2196F3")
```

### 2. Support Dark Mode

```python
# Always provide both themes
page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)
page.dark_theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)
```

### 3. Use Semantic Colors

```python
# Good - Semantic
ft.Text("Error", color=ft.Colors.ERROR)

# Avoid - Arbitrary
ft.Text("Error", color="#F44336")
```

### 4. Theme Consistency

```python
# Apply theme at start, don't change frequently
page.theme = my_theme  # Do this once

# Avoid - Frequent theme changes
def update():
    page.theme = random_theme()  # Don't do this
```

## Next Steps

With theming covered:

1. Build async applications
2. Work with forms and validation
3. Implement drag and drop
4. Add animations
5. Build polished applications
