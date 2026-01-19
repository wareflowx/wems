# Core Concepts

Understanding Flet's core concepts is essential for building effective applications. This guide explains the fundamental building blocks and patterns you'll use in every Flet app.

## The Page Control

The `Page` control is the root of every Flet application. It serves as the main container and provides the interface to the application window and platform capabilities.

### Page Properties

```python
import flet as ft

def main(page: ft.Page):
    # Window properties
    page.title = "My Application"
    page.window_width = 800
    page.window_height = 600
    page.window_min_width = 400
    page.window_min_height = 300
    page.window_center()
    page.window_resizable = True

    # Appearance
    page.bgcolor = ft.Colors.WHITE
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT

    # Layout
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

ft.run(main)
```

### Page Lifecycle Events

```python
def main(page: ft.Page):
    def on_page_resize(e):
        print(f"New size: {page.window_width}x{page.window_height}")

    def on_route_change(e: ft.RouteChangeEvent):
        print(f"Route changed to: {e.route}")

    page.on_resize = on_page_resize
    page.on_route_change = on_route_change
    page.update()

ft.run(main)
```

### Platform Detection

```python
def main(page: ft.Page):
    if page.web:
        print("Running in web browser")
    elif page.platform in ["android", "ios"]:
        print("Running on mobile")
    else:
        print("Running on desktop")
```

## Controls (Widgets)

Controls are the UI building blocks in Flet. Every visible element is a control.

### Control Structure

All controls share these characteristics:

1. **Properties** - Define appearance and behavior
2. **Events** - Respond to user interactions
3. **Methods** - Perform actions
4. **Child Controls** - Container controls can hold other controls

### Creating Controls

```python
# Create a button control
button = ft.Button(
    text="Click me",
    bgcolor=ft.Colors.BLUE,
    color=ft.Colors.WHITE,
    width=200,
    height=50,
    on_click=lambda e: print("Clicked!")
)

# Create a text control
text = ft.Text(
    "Hello, World!",
    size=24,
    weight=ft.FontWeight.BOLD,
    color=ft.Colors.BLACK
)
```

### Referencing Controls

Store control references to modify them later:

```python
def main(page: ft.Page):
    # Create controls with references
    counter_text = ft.Text("0", size=50)
    input_field = ft.TextField(label="Enter text")

    def increment(e):
        counter_text.value = str(int(counter_text.value) + 1)
        page.update()

    page.add(
        counter_text,
        ft.Button("Increment", on_click=increment)
    )

ft.run(main)
```

## Event Handling

Events are how controls communicate user interactions to your code.

### Event Handlers

Event handlers are functions called when events occur:

```python
def handle_click(e):
    # e is the event object
    print(f"Control: {e.control}")
    print(f"Page: {e.page}")

button = ft.Button("Click me", on_click=handle_click)
```

### Lambda Functions

For simple operations, use lambda functions:

```python
button = ft.Button(
    "Click me",
    on_click=lambda e: print("Button clicked!")
)
```

### Common Events

| Event | Description | Controls |
|-------|-------------|----------|
| `on_click` | User tapped/clicked | Button, IconButton, etc. |
| `on_change` | Value changed | TextField, Dropdown, Slider |
| `on_focus` | Control gained focus | TextField, etc. |
| `on_blur` | Control lost focus | TextField, etc. |
| `on_submit` | Form submitted | TextField with `on_submit=True` |

### Event Object Properties

```python
def handle_event(e):
    print(f"Control: {e.control}")      # The control that triggered
    print(f"Page: {e.page}")            # The page instance
    print(f"Data: {e.data}")            # Event-specific data

button = ft.Button("Click", on_click=handle_event)
```

## The Control Tree

Flet builds UIs as a tree of controls:

```
Page (root)
└── Column
    ├── Text "Welcome"
    ├── TextField
    └── Row
        ├── Button "OK"
        └── Button "Cancel"
```

### Adding Controls to Page

```python
page.add(control1, control2, control3)

# Or add a list
page.add(
    ft.Text("Line 1"),
    ft.Text("Line 2"),
    ft.Text("Line 3")
)
```

### Removing Controls

```python
# Remove specific control
page.remove(control_to_remove)

# Remove all controls
page.clean()
```

### Updating the UI

Flet uses an **imperative update model**. Changes don't appear until you call `page.update()`:

```python
# Make multiple changes
text.value = "New text"
button.visible = False
page.bgcolor = ft.Colors.GREY_100

# Apply all changes at once
page.update()
```

**When to call `page.update()`:**
- After modifying control properties
- After adding/removing controls
- After changing page properties
- After any visual change

## Layout Controls

Layout controls organize and position child controls.

### Column

Arranges children vertically:

```python
page.add(
    ft.Column(
        controls=[
            ft.Text("First"),
            ft.Text("Second"),
            ft.Text("Third")
        ],
        alignment=ft.MainAxisAlignment.CENTER,    # Vertical alignment
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # Horizontal
        spacing=10,                               # Space between children
        run_spacing=20,                           # Space between runs
    )
)
```

### Row

Arranges children horizontally:

```python
page.add(
    ft.Row(
        controls=[
            ft.Button("Button 1"),
            ft.Button("Button 2"),
            ft.Button("Button 3")
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        spacing=10
    )
)
```

### Container

A versatile container with padding, margin, and decoration:

```python
page.add(
    ft.Container(
        content=ft.Text("Boxed text"),
        padding=20,
        margin=10,
        bgcolor=ft.Colors.BLUE_100,
        border_radius=10,
        width=200,
        height=100,
        alignment=ft.alignment.center
    )
)
```

### Stack

Overlays children on top of each other:

```python
page.add(
    ft.Stack(
        controls=[
            ft.Image(src="background.png", width=300, height=300),
            ft.Text("Overlay text", size=30)
        ],
        width=300,
        height=300
    )
)
```

## State Management

State management in Flet is about managing data and keeping the UI in sync.

### Local State

Store state in variables and update the UI:

```python
def main(page: ft.Page):
    count = 0
    count_text = ft.Text("0", size=50)

    def increment(e):
        nonlocal count
        count += 1
        count_text.value = str(count)
        page.update()

    page.add(
        count_text,
        ft.Button("Increment", on_click=increment)
    )

ft.run(main)
```

### Control References as State

Controls themselves can hold state:

```python
def main(page: ft.Page):
    text_field = ft.TextField(label="Enter text")
    display = ft.Text("")

    def update_display(e):
        display.value = f"You typed: {text_field.value}"
        page.update()

    text_field.on_change = update_display

    page.add(text_field, display)

ft.run(main)
```

### State Classes

For complex state, create a state class:

```python
class AppState:
    def __init__(self, page: ft.Page):
        self.page = page
        self.counter = 0
        self.todos = []

    def increment_counter(self):
        self.counter += 1
        self.update_ui()

    def update_ui(self):
        # Update all controls that depend on state
        pass

def main(page: ft.Page):
    state = AppState(page)
    # Build UI using state
    pass

ft.run(main)
```

## Responsive Design

Make apps adapt to different screen sizes.

### ResponsiveRow

```python
page.add(
    ft.ResponsiveRow(
        controls=[
            ft.Container(
                ft.Text("Column 1"),
                col={"sm": 6, "md": 4, "xl": 3}
            ),
            ft.Container(
                ft.Text("Column 2"),
                col={"sm": 6, "md": 4, "xl": 3}
            ),
        ]
    )
)
```

### Window Size Detection

```python
def main(page: ft.Page):
    def on_resize(e):
        if page.window_width < 600:
            layout = "mobile"
        else:
            layout = "desktop"
        print(f"Layout: {layout}")

    page.on_resize = on_resize
    page.update()

ft.run(main)
```

## User Sessions

Each connected user has their own Page instance and session.

### Session Properties

```python
def main(page: ft.Page):
    # Get session ID
    session_id = page.session.id

    # Get client IP
    client_ip = page.client_ip

    # Get user agent
    user_agent = page.client_user_agent

    print(f"Session: {session_id}")
    print(f"IP: {client_ip}")
    print(f"User Agent: {user_agent}")
```

### Session Storage

Store data per session:

```python
def main(page: ft.Page):
    # Store data in session
    page.session.set("user_id", "12345")

    # Retrieve data
    user_id = page.session.get("user_id")
```

## Best Practices

### 1. Use Descriptive Variable Names

```python
# Good
submit_button = ft.Button("Submit", on_click=handle_submit)

# Avoid
b = ft.Button("Submit")
```

### 2. Keep Event Handlers Simple

```python
# Good
def handle_submit(e):
    data = validate_form()
    if data:
        save_data(data)
        show_success_message()

# Avoid
def handle_submit(e):
    # 100 lines of logic
```

### 3. Batch Updates

```python
# Good - single update
text.value = "New"
button.visible = False
page.update()

# Avoid - multiple updates
text.value = "New"
page.update()
button.visible = False
page.update()
```

### 4. Use Type Hints

```python
def main(page: ft.Page) -> None:
    def handle_click(e: ft.ControlEvent) -> None:
        pass

    button = ft.Button("Click", on_click=handle_click)
```

### 5. Separate UI from Logic

```python
# UI
def build_ui(page: ft.Page, state: AppState):
    page.add(
        ft.Text("My App"),
        create_form(state),
        create_button(state)
    )

# Logic
class AppState:
    def process_data(self):
        # Business logic here
        pass
```

## Common Patterns

### Pattern 1: Loading Overlay

```python
def main(page: ft.Page):
    main_content = ft.Column([ft.Text("Content")])
    loader = ft.ProgressRing(visible=False)

    def load_data(e):
        loader.visible = True
        page.update()

        # Simulate loading
        time.sleep(1)

        loader.visible = False
        page.update()

    page.add(
        ft.Stack([
            main_content,
            loader
        ])
    )
```

### Pattern 2: Form Validation

```python
def main(page: ft.Page):
    name = ft.TextField(label="Name")
    email = ft.TextField(label="Email")
    error_text = ft.Text("", color=ft.Colors.RED)

    def validate_and_submit(e):
        if not name.value:
            error_text.value = "Name is required"
            page.update()
            return

        if "@" not in email.value:
            error_text.value = "Invalid email"
            page.update()
            return

        error_text.value = "Valid!"
        page.update()

    page.add(name, email, error_text, ft.Button("Submit", on_click=validate_and_submit))
```

### Pattern 3: Dynamic Lists

```python
def main(page: ft.Page):
    items = []
    list_view = ft.Column()

    def add_item(e):
        new_item = ft.Text(f"Item {len(items) + 1}")
        items.append(new_item)
        list_view.controls.append(new_item)
        page.update()

    page.add(
        list_view,
        ft.Button("Add Item", on_click=add_item)
    )
```

## Next Steps

Now that you understand Flet's core concepts:

1. Learn about specific controls and their properties
2. Master layouts for responsive design
3. Implement state management patterns
4. Handle complex user interactions
5. Build your first complete application
