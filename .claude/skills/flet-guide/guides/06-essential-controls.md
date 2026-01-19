# Essential UI Controls

Flet provides a comprehensive set of UI controls for building applications. This guide covers the essential controls you'll use most frequently.

## Text Display Controls

### Text

The `Text` control displays formatted text content.

```python
import flet as ft

def main(page: ft.Page):
    page.add(
        ft.Text(
            "Hello, World!",
            size=30,                    # Font size
            weight=ft.FontWeight.BOLD,  # Font weight
            color=ft.Colors.BLUE,       # Text color
            italic=True,                # Italic style
            max_lines=2,                # Maximum lines before ellipsis
            overflow=ft.TextOverflow.ELLIPSIS,
            text_align=ft.TextAlign.CENTER,
            selectable=True,            # Allow text selection
        )
    )

ft.run(main)
```

### Rich Text with TextSpan

```python
def main(page: ft.Page):
    page.add(
        ft.Text(
            spans=[
            ft.TextSpan(
                "Hello, ",
                ft.TextStyle(
                    size=30,
                    color=ft.Colors.BLACK
                )
            ),
            ft.TextSpan(
                "Flet!",
                ft.TextStyle(
                    size=30,
                    color=ft.Colors.BLUE,
                    weight=ft.FontWeight.BOLD,
                    decoration=ft.TextDecoration.UNDERLINE
                )
            ),
        ])
    )

ft.run(main)
```

### Icon

```python
def main(page: ft.Page):
    page.add(
        ft.Row(
            [
                ft.Icon(ft.Icons.HOME, size=50, color=ft.Colors.BLUE),
                ft.Icon(ft.Icons.SEARCH, size=50, color=ft.Colors.RED),
                ft.Icon(ft.Icons.PERSON, size=50, color=ft.Colors.GREEN),
            ],
            spacing=20
        )
    )

ft.run(main)
```

### Image

```python
def main(page: ft.Page):
    page.add(
        ft.Image(
            src="/icons/icon_192.png",  # Relative path to assets
            width=200,
            height=200,
            fit=ft.ImageFit.CONTAIN,    # CONTAIN, COVER, FILL, FIT_WIDTH, FIT_HEIGHT, NONE
            repeat=ft.ImageRepeat.NO_REPEAT,
            border_radius=10,
        )
    )

ft.run(main)
```

## Input Controls

### TextField

Single-line text input field.

```python
def main(page: ft.Page):
    def handle_change(e):
        print(f"Input value: {text_field.value}")

    def handle_submit(e):
        print(f"Submitted: {text_field.value}")

    text_field = ft.TextField(
        label="Username",
        hint_text="Enter your username",
        prefix_icon=ft.Icons.PERSON,
        suffix_icon=ft.Icons.CHECK,
        suffix_icon_color=ft.Colors.GREEN,
        value="",
        text_align=ft.TextAlign.LEFT,
        max_length=20,
        password=False,
        can_reveal_password=False,
        keyboard_type=ft.KeyboardType.TEXT,
        capitalization=ft.TextCapitalization.NONE,
        autofocus=True,
        on_change=handle_change,
        on_submit=handle_submit,
        border=ft.border.InputBorder.OUTLINE,
        border_radius=20,
    )

    page.add(text_field)

ft.run(main)
```

### Multiline TextField

```python
def main(page: ft.Page):
    page.add(
        ft.TextField(
            label="Description",
            multiline=True,
            min_lines=3,
            max_lines=10,
            text_align=ft.TextAlign.LEFT,
        )
    )

ft.run(main)
```

### Password Field with Reveal

```python
def main(page: ft.Page):
    page.add(
        ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
        )
    )

ft.run(main)
```

### Dropdown

```python
def main(page: ft.Page):
    def handle_change(e):
        print(f"Selected: {dropdown.value}")

    dropdown = ft.Dropdown(
        label="Choose option",
        hint_text="Select one",
        options=[
            ft.dropdown.Option("Option 1"),
            ft.dropdown.Option("Option 2"),
            ft.dropdown.Option("Option 3"),
        ],
        value=None,
        on_change=handle_change,
        width=200,
    )

    page.add(dropdown)

ft.run(main)
```

## Selection Controls

### Checkbox

```python
def main(page: ft.Page):
    def handle_change(e):
        print(f"Checkbox checked: {checkbox.value}")

    checkbox = ft.Checkbox(
        label="Accept terms and conditions",
        value=False,
        tristate=False,
        on_change=handle_change,
    )

    page.add(checkbox)

ft.run(main)
```

### Switch

```python
def main(page: ft.Page):
    def handle_change(e):
        print(f"Switch: {switch.value}")

    switch = ft.Switch(
        label="Enable notifications",
        value=False,
        on_change=handle_change,
    )

    page.add(switch)

ft.run(main)
```

### Radio Group

```python
def main(page: ft.Page):
    def handle_change(e):
        print(f"Selected: {radio_group.value}")

    radio_group = ft.RadioGroup(
        content=ft.Column([
            ft.Radio(value="option1", label="Option 1"),
            ft.Radio(value="option2", label="Option 2"),
            ft.Radio(value="option3", label="Option 3"),
        ]),
        value="option1",
        on_change=handle_change,
    )

    page.add(radio_group)

ft.run(main)
```

### Slider

```python
def main(page: ft.Page):
    def handle_change(e):
        print(f"Slider value: {slider.value}")

    slider = ft.Slider(
        min_value=0,
        max_value=100,
        value=50,
        divisions=10,  # Number of discrete steps
        label="{value}%",
        on_change=handle_change,
        width=300,
    )

    page.add(
        ft.Column([
            slider,
            ft.Text(f"Value: {slider.value}"),
        ], spacing=20)
    )

ft.run(main)
```

## Button Controls

### ElevatedButton

```python
def main(page: ft.Page):
    def handle_click(e):
        print("Button clicked!")

    page.add(
        ft.ElevatedButton(
            "Click me",
            on_click=handle_click,
            bgcolor=ft.Colors.BLUE,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.padding.all(20),
            ),
        )
    )

ft.run(main)
```

### TextButton

```python
def main(page: ft.Page):
    page.add(
        ft.TextButton(
            "Text Button",
            on_click=lambda e: print("Clicked!"),
        )
    )

ft.run(main)
```

### OutlinedButton

```python
def main(page: ft.Page):
    page.add(
        ft.OutlinedButton(
            "Outlined Button",
            on_click=lambda e: print("Clicked!"),
        )
    )

ft.run(main)
```

### FilledButton

```python
def main(page: ft.Page):
    page.add(
        ft.FilledButton(
            "Filled Button",
            on_click=lambda e: print("Clicked!"),
        )
    )

ft.run(main)
```

### IconButton

```python
def main(page: ft.Page):
    page.add(
        ft.Row(
            [
                ft.IconButton(
                    ft.Icons.HOME,
                    on_click=lambda e: print("Home"),
                    tooltip="Home",
                ),
                ft.IconButton(
                    ft.Icons.SEARCH,
                    on_click=lambda e: print("Search"),
                    tooltip="Search",
                ),
                ft.IconButton(
                    ft.Icons.SETTINGS,
                    on_click=lambda e: print("Settings"),
                    tooltip="Settings",
                ),
            ],
            spacing=10
        )
    )

ft.run(main)
```

### FloatingActionButton

```python
def main(page: ft.Page):
    page.add(
        ft.FloatingActionButton(
            ft.Icons.ADD,
            on_click=lambda e: print("Add"),
            bgcolor=ft.Colors.BLUE,
            foreground_color=ft.Colors.WHITE,
        )
    )

ft.run(main)
```

## Progress Indicators

### ProgressBar

```python
def main(page: ft.Page):
    progress_bar = ft.ProgressBar(
        width=400,
        bar_height=20,
        bgcolor=ft.Colors.GREY_200,
        color=ft.Colors.BLUE,
        value=0.5,  # 0.0 to 1.0
    )

    page.add(progress_bar)

ft.run(main)
```

### ProgressRing

```python
def main(page: ft.Page):
    page.add(
        ft.ProgressRing(
            width=40,
            height=40,
            stroke_width=4,
            bgcolor=ft.Colors.GREY_200,
            value=0.5,  # None for indeterminate
        )
    )

ft.run(main)
```

### CircularProgressIndicator

```python
def main(page: ft.Page):
    page.add(
        ft.Column(
            [
                ft.CircularProgressIndicator(
                    width=40,
                    height=40,
                    stroke_width=4,
                ),
                ft.LinearProgressIndicator(
                    width=400,
                    color=ft.Colors.BLUE,
                ),
            ],
            spacing=20
        )
    )

ft.run(main)
```

## Common Patterns

### Form with Validation

```python
def main(page: ft.Page):
    name = ft.TextField(label="Name")
    email = ft.TextField(label="Email")
    phone = ft.TextField(label="Phone")
    error_text = ft.Text("", color=ft.Colors.RED)

    def validate_and_submit(e):
        errors = []

        if not name.value:
            errors.append("Name is required")
        elif len(name.value) < 2:
            errors.append("Name must be at least 2 characters")

        if not email.value:
            errors.append("Email is required")
        elif "@" not in email.value:
            errors.append("Invalid email format")

        if errors:
            error_text.value = "\n".join(errors)
        else:
            error_text.value = "Form submitted successfully!"
            error_text.color = ft.Colors.GREEN

        page.update()

    page.add(
        ft.Column([
            ft.Text("Contact Form", size=30, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20),
            name,
            email,
            phone,
            ft.ElevatedButton("Submit", on_click=validate_and_submit),
            error_text,
        ], spacing=10)
    )

ft.run(main)
```

### Search Bar with Results

```python
def main(page: ft.Page):
    def handle_search(e):
        search_term = search_field.value.lower()
        results.controls.clear()

        if not search_term:
            results.controls.append(ft.Text("Enter a search term"))
        else:
            for i in range(5):
                results.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.SEARCH),
                        title=ft.Text(f"Result {i+1} for '{search_field.value}'"),
                        on_click=lambda e, item=i: print(f"Clicked item {item+1}"),
                    )
                )

        page.update()

    search_field = ft.TextField(
        hint_text="Search...",
        prefix_icon=ft.Icons.SEARCH,
        on_submit=handle_search,
        expand=True,
    )

    results = ft.Column([
        ft.Text("Enter a search term", color=ft.Colors.GREY)
    ])

    page.add(
        ft.Column([
            ft.Row([search_field], spacing=10),
            ft.Divider(height=20),
            results,
        ])
    )

ft.run(main)
```

### Labeled Input Groups

```python
def main(page: ft.Page):
    def create_labeled_input(label, hint, icon):
        return ft.Column([
            ft.Text(label, size=14, weight=ft.FontWeight.BOLD),
            ft.TextField(
                hint_text=hint,
                prefix_icon=icon,
                border=ft.border.InputBorder.UNDERLINE,
            ),
        ], spacing=5)

    page.add(
        ft.Column([
            create_labeled_input("Full Name", "John Doe", ft.Icons.PERSON),
            create_labeled_input("Email", "john@example.com", ft.Icons.EMAIL),
            create_labeled_input("Phone", "+1 234 567 8900", ft.Icons.PHONE),
        ], spacing=20)
    )

ft.run(main)
```

## Button Styling Examples

```python
def main(page: ft.Page):
    page.add(
        ft.Column([
            ft.Text("Button Styles", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20),

            # Different button types
            ft.ElevatedButton("Elevated"),
            ft.TextButton("Text"),
            ft.OutlinedButton("Outlined"),
            ft.FilledButton("Filled"),

            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),

            # Custom styled buttons
            ft.ElevatedButton(
                "Custom 1",
                bgcolor=ft.Colors.RED,
                color=ft.Colors.WHITE,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=20),
                    padding=ft.padding.symmetric(horizontal=30, vertical=20),
                ),
            ),

            ft.ElevatedButton(
                "Custom 2",
                bgcolor=ft.Colors.GREEN,
                color=ft.Colors.WHITE,
                style=ft.ButtonStyle(
                    shape=ft.BeveledRectangleBorder(),
                ),
            ),

            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),

            # Icon buttons
            ft.Row([
                ft.ElevatedButton(
                    "Left Icon",
                    icon=ft.Icons.ARROW_BACK,
                ),
                ft.ElevatedButton(
                    "Right Icon",
                    icon=ft.Icons.ARROW_FORWARD,
                    icon_color=ft.Colors.WHITE,
                ),
            ], spacing=10),

        ], spacing=10)
    )

ft.run(main)
```

## Best Practices

### 1. Use Meaningful Labels

```python
# Good
ft.TextField(label="Email Address", hint_text="user@example.com")

# Avoid
ft.TextField(label="Input")
```

### 2. Provide Feedback

```python
def handle_click(e):
    button.text = "Loading..."
    button.disabled = True
    page.update()

    # Perform action
    time.sleep(1)

    button.text = "Done!"
    page.update()
```

### 3. Use Icons Appropriately

Icons should be meaningful and aid understanding:

```python
# Good
ft.TextField(label="Search", prefix_icon=ft.Icons.SEARCH)

# Avoid
ft.TextField(label="Search", prefix_icon=ft.Icons.DELETE)
```

### 4. Group Related Inputs

```python
# Good - Grouped
ft.Container(
    ft.Column([name, email, phone]),
    border=ft.border.all(1, ft.Colors.GREY),
    border_radius=10,
    padding=20,
)

# Avoid - Ungrouped
page.add(name, email, phone)
```

### 5. Set Appropriate Widths

```python
# Good - Constrained width
ft.TextField(width=300)

# Avoid - Full width when not needed
ft.TextField(expand=True)
```

## Next Steps

Now that you understand essential controls:

1. Learn advanced controls for complex UIs
2. Master dialogs and popups
3. Implement navigation patterns
4. Style controls with theming
5. Handle complex user interactions
