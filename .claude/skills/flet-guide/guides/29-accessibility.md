# Accessibility

Build inclusive Flet applications that work for everyone, including users with disabilities.

## Semantic Labels

### Provide Accessible Labels

```python
import flet as ft

def main(page: ft.Page):
    page.add(
        ft.Image(
            src="/path/to/image.png",
            # Screen reader will read this
            semantic_label="Company logo",
        )
    )

ft.run(main)
```

## Screen Reader Support

### Accessible Controls

```python
def main(page: ft.Page):
    page.add(
        ft.TextField(
            label="Email address",
            # Hint for screen readers
            semantic_label="Enter your email address"
        )
    )

ft.run(main)
```

## Keyboard Navigation

### Keyboard Shortcuts

```python
def main(page: ft.Page):
    def handle_key(e):
        if e.key == "S" and e.ctrl:
            # Ctrl+S to save
            save_file()

    page.on_keyboard_event = handle_key

ft.run(main)
```

### Tab Order

```python
def main(page: ft.Page):
    # Controls are automatically in tab order
    page.add(
        ft.TextField(label="First"),
        ft.TextField(label="Second"),
        ft.Button("Submit"),
    )

ft.run(main)
```

## Semantics Service

### Screen Reader Announcements

```python
def main(page: ft.Page):
    semantics = page.semantics

    def announce(message):
        # Announce to screen reader
        semantics.announce(message)

    def handle_click(e):
        announce("Button clicked")

    page.add(
        ft.Button("Click me", on_click=handle_click)
    )

ft.run(main)
```

## Focus Management

### Programmatic Focus

```python
def main(page: ft.Page):
    name_field = ft.TextField(label="Name")
    email_field = ft.TextField(label="Email")

    def set_initial_focus(e):
        # Focus first field
        page.set_focus()

    page.add(name_field, email_field)
    page.set_focus()

ft.run(main)
```

## Color Contrast

### Ensure Readability

```python
def main(page: ft.Page):
    # Good contrast ratios
    page.add(
        ft.Text(
            "High contrast text",
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLACK,
        )
    )

ft.run(main)
```

## Best Practices

### 1. Provide Alternative Text

```python
# Good - Alternative text
ft.Image(
    src="chart.png",
    semantic_label="Sales chart showing 50% increase"
)
```

### 2. Support Keyboard

```python
# Ensure all actions are keyboard accessible
ft.Button(
    "Submit",
    # Can be activated with Enter/Space
    on_click=submit_form
)
```

### 3. Use Semantic HTML

```python
# Use appropriate controls for meaning
ft.RadioButton()  # Not ft.Checkbox for single choice
```

### 4. Test Accessibility

```bash
# Test with screen reader
# Test keyboard navigation
# Check color contrast
```

## WCAG Guidelines

Follow Web Content Accessibility Guidelines:
- **Level A**: Basic accessibility
- **Level AA**: Enhanced accessibility (recommended)
- **Level AAA**: Highest accessibility

## Next Steps

1. Follow best practices
2. Build production apps
3. Deploy applications
4. Monitor accessibility
