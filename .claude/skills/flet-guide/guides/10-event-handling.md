# Event Handling

Events are how Flet controls communicate user interactions to your application code. Mastering event handling is crucial for building interactive applications.

## Understanding Events

In Flet, events are triggered by user interactions like clicks, text changes, focus changes, etc. You attach **event handlers** to controls to respond to these events.

### Basic Event Handler

```python
import flet as ft

def main(page: ft.Page):
    def handle_click(e):
        print("Button clicked!")

    button = ft.Button("Click me", on_click=handle_click)
    page.add(button)

ft.run(main)
```

## The Event Object

Event handlers receive an event object containing information about the event:

```python
def handle_event(e):
    print(f"Control: {e.control}")      # The control that triggered
    print(f"Page: {e.page}")            # The page instance
    print(f"Data: {e.data}")            # Event-specific data
    print(f"Target: {e.target}")        # Target control

button = ft.Button("Click", on_click=handle_event)
```

## Common Events

### onClick

Triggered when a button or clickable control is tapped:

```python
def main(page: ft.Page):
    def handle_button_click(e):
        print("Button clicked!")
        # Access the button that was clicked
        e.control.text = "Clicked!"
        page.update()

    page.add(
        ft.ElevatedButton(
            "Click me",
            on_click=handle_button_click
        )
    )

ft.run(main)
```

### onChange

Triggered when the value of a control changes:

```python
def main(page: ft.Page):
    def handle_text_change(e):
        print(f"Text changed to: {text_field.value}")

    text_field = ft.TextField(
        label="Type something",
        on_change=handle_text_change
    )

    page.add(text_field)

ft.run(main)
```

### onFocus and onBlur

```python
def main(page: ft.Page):
    def handle_focus(e):
        print("Field focused")
        e.control.bgcolor = ft.Colors.BLUE_50
        page.update()

    def handle_blur(e):
        print("Field lost focus")
        e.control.bgcolor = None
        page.update()

    page.add(
        ft.TextField(
            label="Focus me",
            on_focus=handle_focus,
            on_blur=handle_blur
        )
    )

ft.run(main)
```

### onSubmit

```python
def main(page: ft.Page):
    def handle_submit(e):
        print(f"Submitted: {text_field.value}")

    text_field = ft.TextField(
        label="Press Enter",
        on_submit=handle_submit
    )

    page.add(text_field)

ft.run(main)
```

## Lambda Functions

For simple handlers, use lambda functions:

```python
def main(page: ft.Page):
    page.add(
        ft.Button(
            "Click me",
            on_click=lambda e: print("Clicked!")
        )
    )

ft.run(main)
```

### Passing Arguments with Lambda

```python
def main(page: ft.Page):
    def handle_click_with_args(e, value):
        print(f"Clicked with value: {value}")

    page.add(
        ft.Row([
            ft.Button("A", on_click=lambda e: handle_click_with_args(e, "A")),
            ft.Button("B", on_click=lambda e: handle_click_with_args(e, "B")),
            ft.Button("C", on_click=lambda e: handle_click_with_args(e, "C")),
        ])
    )

ft.run(main)
```

## Control References

Store control references to access them in event handlers:

```python
def main(page: ft.Page):
    # Create controls with references
    text_field = ft.TextField(label="Enter text")
    display = ft.Text("")

    def update_display(e):
        # Access control by reference
        display.value = f"You typed: {text_field.value}"
        page.update()

    text_field.on_change = update_display

    page.add(text_field, display)

ft.run(main)
```

## Multiple Events on Same Control

```python
def main(page: ft.Page):
    text_field = ft.TextField(
        label="Multiple events",
        on_change=lambda e: print("Changed"),
        on_focus=lambda e: print("Focused"),
        on_blur=lambda e: print("Blurred"),
        on_submit=lambda e: print("Submitted"),
    )

    page.add(text_field)

ft.run(main)
```

## Event Propagation

Events can propagate through the control tree:

```python
def main(page: ft.Page):
    def handle_row_click(e):
        print("Row clicked")

    def handle_button_click(e):
        print("Button clicked")
        # Stop propagation
        e.stop_propagation()

    page.add(
        ft.Row(
            [
                ft.Container(
                    ft.Button("Click me", on_click=handle_button_click),
                    on_click=handle_row_click,
                )
            ]
        )
    )

ft.run(main)
```

## Conditional Event Handling

```python
def main(page: ft.Page):
    counter = 0
    button = ft.Button("Click me", disabled=False)

    def handle_click(e):
        nonlocal counter
        counter += 1

        if counter >= 5:
            button.disabled = True
            button.text = "Limit reached"

        page.update()

    button.on_click = handle_click
    page.add(button)

ft.run(main)
```

## Event Handlers with UI Updates

```python
def main(page: ft.Page):
    count = 0
    counter_text = ft.Text("0", size=50)

    def increment(e):
        nonlocal count
        count += 1
        counter_text.value = str(count)
        # Update UI after all changes
        page.update()

    page.add(
        counter_text,
        ft.Button("Increment", on_click=increment)
    )

ft.run(main)
```

## Handling Events Across Multiple Controls

```python
def main(page: ft.Page):
    buttons = []

    def handle_button_click(e, index):
        # Access the specific button
        button = buttons[index]
        button.text = f"Button {index} clicked!"
        button.bgcolor = ft.Colors.BLUE
        page.update()

    for i in range(5):
        button = ft.Button(
            f"Button {i}",
            on_click=lambda e, idx=i: handle_button_click(e, idx)
        )
        buttons.append(button)

    page.add(ft.Row(buttons))

ft.run(main)
```

## Event Handlers with Confirmation

```python
def main(page: ft.Page):
    def handle_delete(e):
        def confirm_delete(confirm_e):
            if confirm_e.control.selected_index == 0:  # Yes
                print("Item deleted")
            page.dialog.open = False
            page.update()

        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Delete"),
            content=ft.Text("Are you sure?"),
            actions=[
                ft.TextButton("Yes", on_click=confirm_delete),
                ft.TextButton("No", on_click=lambda e: close_dialog()),
            ]
        )
        page.dialog.open = True
        page.update()

    def close_dialog():
        page.dialog.open = False
        page.update()

    page.add(
        ft.Button(
            "Delete",
            on_click=handle_delete,
            bgcolor=ft.Colors.RED,
            color=ft.Colors.WHITE
        )
    )

ft.run(main)
```

## Async Event Handlers

For async operations, use async handlers:

```python
import asyncio
import flet as ft

async def main(page: ft.Page):
    async def handle_click(e):
        # Show loading state
        button.text = "Loading..."
        button.disabled = True
        page.update()

        # Simulate async operation
        await asyncio.sleep(2)

        # Update UI
        button.text = "Done!"
        page.update()

        # Reset after delay
        await asyncio.sleep(1)
        button.text = "Click me"
        button.disabled = False
        page.update()

    button = ft.Button("Click me", on_click=handle_click)
    page.add(button)

ft.run(main)
```

## Common Patterns

### Toggle Button

```python
def main(page: ft.Page):
    is_active = False
    toggle_button = ft.Button("Off", bgcolor=ft.Colors.GREY)

    def toggle(e):
        nonlocal is_active
        is_active = not is_active

        if is_active:
            toggle_button.text = "On"
            toggle_button.bgcolor = ft.Colors.GREEN
        else:
            toggle_button.text = "Off"
            toggle_button.bgcolor = ft.Colors.GREY

        page.update()

    toggle_button.on_click = toggle
    page.add(toggle_button)

ft.run(main)
```

### Counter with Multiple Buttons

```python
def main(page: ft.Page):
    counter = 0
    counter_text = ft.Text("0", size=50)

    def change(e, delta):
        nonlocal counter
        counter += delta
        counter_text.value = str(counter)
        page.update()

    page.add(
        counter_text,
        ft.Row([
            ft.Button("Decrement", on_click=lambda e: change(e, -1)),
            ft.Button("Increment", on_click=lambda e: change(e, 1)),
        ])
    )

ft.run(main)
```

### Form Validation on Submit

```python
def main(page: ft.Page):
    name = ft.TextField(label="Name")
    email = ft.TextField(label="Email")
    error_text = ft.Text("", color=ft.Colors.RED)

    def validate_and_submit(e):
        errors = []

        if not name.value:
            errors.append("Name is required")

        if not email.value or "@" not in email.value:
            errors.append("Valid email required")

        if errors:
            error_text.value = "\n".join(errors)
        else:
            error_text.value = "Form submitted!"
            error_text.color = ft.Colors.GREEN
            # Process form
            print(f"Name: {name.value}, Email: {email.value}")

        page.update()

    submit_button = ft.Button("Submit", on_click=validate_and_submit)

    page.add(
        name,
        email,
        error_text,
        submit_button
    )

ft.run(main)
```

### Dynamic Button Creation

```python
def main(page: ft.Page):
    display = ft.Text("Select an option")

    def handle_option_click(e, option):
        display.value = f"Selected: {option}"
        page.update()

    options = ["Option A", "Option B", "Option C"]

    buttons = [
        ft.Button(
            option,
            on_click=lambda e, opt=option: handle_option_click(e, opt)
        )
        for option in options
    ]

    page.add(
        display,
        ft.Column(buttons, spacing=10)
    )

ft.run(main)
```

### Debounced Input

```python
import asyncio

def main(page: ft.Page):
    search_field = ft.TextField(label="Search")
    results = ft.Text("Start typing...")

    async def debounced_search():
        await asyncio.sleep(0.5)  # Wait 500ms
        results.value = f"Results for: {search_field.value}"
        page.update()

    async def handle_change(e):
        # Cancel previous search if running
        if hasattr(handle_change, 'task'):
            handle_change.task.cancel()

        # Start new debounced search
        handle_change.task = asyncio.create_task(debounced_search())

    search_field.on_change = handle_change

    page.add(search_field, results)

ft.run(main)
```

## Best Practices

### 1. Keep Event Handlers Focused

```python
# Good - Single responsibility
def handle_click(e):
    process_click()
    update_ui()

# Avoid - Too many responsibilities
def handle_click(e):
    # 50 lines of logic
```

### 2. Use Type Hints

```python
def handle_click(e: ft.ControlEvent) -> None:
    print("Clicked")
```

### 3. Handle Errors Gracefully

```python
def handle_click(e):
    try:
        # Operation that might fail
        risky_operation()
    except Exception as ex:
        page.snack_bar = ft.SnackBar(
            ft.Text(f"Error: {str(ex)}"),
            bgcolor=ft.Colors.RED
        )
        page.snack_bar.open = True
        page.update()
```

### 4. Avoid Blocking Operations

```python
# Bad - Blocks UI
def handle_click(e):
    time.sleep(5)  # Don't do this!
    print("Done")

# Good - Use async
async def handle_click(e):
    await asyncio.sleep(5)
    print("Done")
```

### 5. Provide User Feedback

```python
def handle_action(e):
    # Show loading state
    button.text = "Processing..."
    button.disabled = True
    page.update()

    # Perform action
    result = process_data()

    # Show result
    button.text = "Done!"
    page.snack_bar = ft.SnackBar(ft.Text("Success!"))
    page.snack_bar.open = True
    page.update()
```

## Next Steps

With event handling mastered:

1. Learn state management patterns
2. Implement complex interactions
3. Work with forms and validation
4. Add animations
5. Build complete applications
