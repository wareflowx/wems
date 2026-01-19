# Best Practices and Patterns

A comprehensive guide to writing clean, maintainable, and performant Flet applications.

## Code Organization

### Project Structure

```
my-flet-app/
├── main.py              # Entry point
├── app/                 # Application code
│   ├── __init__.py
│   ├── views/           # UI views
│   ├── models/          # Data models
│   ├── services/        # Business logic
│   └── utils/           # Utilities
├── assets/              # Images, fonts
├── tests/               # Tests
└── requirements.txt     # Dependencies
```

### Separation of Concerns

```python
# models/user.py
class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email

# views/user_view.py
def build_user_profile(user):
    return ft.Column([
        ft.Text(user.username),
        ft.Text(user.email),
    ])

# main.py
def main(page: ft.Page):
    user = User("john", "john@example.com")
    page.add(build_user_profile(user))

ft.run(main)
```

## Performance

### Efficient Updates

```python
# Good - Batch updates
def update_ui():
    control1.value = "Value 1"
    control2.value = "Value 2"
    control3.visible = False
    page.update()  # Single update

# Avoid - Multiple updates
def update_ui():
    control1.value = "Value 1"
    page.update()  # Update 1
    control2.value = "Value 2"
    page.update()  # Update 2
```

### Lazy Loading

```python
def main(page: ft.Page):
    # Load views only when needed
    def load_settings():
        from views.settings import settings_view
        return settings_view()

    page.add(
        ft.Button("Settings", on_click=lambda e: page.add(load_settings()))
    )

ft.run(main)
```

### Control Reuse

```python
# Good - Reusable components
def create_card(title, content):
    return ft.Card(
        content=ft.Container(
            ft.Column([
                ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text(content),
            ]),
            padding=20
        )
    )

# Use throughout app
page.add(create_card("Card 1", "Content 1"))
page.add(create_card("Card 2", "Content 2"))
```

## Error Handling

### Graceful Degradation

```python
def main(page: ft.Page):
    def risky_operation():
        try:
            # Operation that might fail
            result = external_api_call()
            return result
        except ConnectionError:
            page.snack_bar = ft.SnackBar(
                ft.Text("Connection error. Please check your internet.")
            )
            page.snack_bar.open = True
            return None
        except Exception as e:
            page.snack_bar = ft.SnackBar(
                ft.Text(f"An error occurred: {str(e)}")
            )
            page.snack_bar.open = True
            return None

ft.run(main)
```

### Validation

```python
def validate_email(email):
    """Validate email format."""
    if not email:
        return False, "Email is required"
    if "@" not in email:
        return False, "Invalid email format"
    return True, ""

def submit_form(email, password):
    # Validate before processing
    valid, error = validate_email(email)
    if not valid:
        return error

    # Process form
    return "Success"
```

## Security

### Input Sanitization

```python
def sanitize_input(text):
    """Remove potentially harmful content."""
    # Remove HTML tags
    import re
    clean = re.sub(r'<[^>]+>', '', text)
    return clean.strip()

def handle_submit(e):
    user_input = text_field.value
    clean_input = sanitize_input(user_input)
    # Use clean_input
```

### Secure Storage

```python
# Never store sensitive data in plain text
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def store_user(username, password):
    hashed = hash_password(password)
    storage.set("password", hashed)
```

## Naming Conventions

### Descriptive Names

```python
# Good - Descriptive
user_email_field = ft.TextField(label="Email")
submit_button = ft.Button("Submit")

# Avoid - Generic
field1 = ft.TextField(label="Email")
button1 = ft.Button("Submit")
```

### Consistent Style

```python
# Choose a convention and stick to it
# snake_case for variables and functions
user_name = "John"
def get_user_data():

# PascalCase for classes
class UserViewModel:
    pass
```

## Documentation

### Docstrings

```python
def calculate_total(items):
    """
    Calculate the total price of all items.

    Args:
        items: List of dictionaries with 'price' key

    Returns:
        float: Total price
    """
    return sum(item['price'] for item in items)
```

### Comments

```python
# Good - Explain why, not what
# Use a set for O(1) lookup
seen_items = set()

# Avoid - Obvious comments
# Increment counter
counter += 1
```

## Testing

### Write Tests

```python
import pytest

def test_user_creation():
    user = User("john", "john@example.com")
    assert user.username == "john"
    assert user.email == "john@example.com"

def test_invalid_email():
    valid, error = validate_email("invalid")
    assert not valid
    assert "Invalid email" in error
```

## Debugging

### Print Debugging

```python
def handle_click(e):
    print(f"Button clicked: {e.control}")
    print(f"Page state: {page.route}")
    # More complex debugging
    import pdb; pdb.set_trace()
```

### Flet Debug Mode

```bash
# Run with debug mode
FLET_DEBUG=true flet run app.py
```

## Anti-Patterns

### Common Mistakes to Avoid

```python
# 1. Forgetting page.update()
control.value = "New value"
# page.update()  # Don't forget!

# 2. Not handling errors
result = risky_operation()  # Might crash

# 3. Hardcoding values
width = 400  # Should be responsive

# 4. Blocking the UI
time.sleep(5)  # Freezes UI, use asyncio instead

# 5. Global state
count = 0  # Use class or page property instead
```

## Performance Tips

### Optimize Lists

```python
# Good - Use ListView for many items
ft.ListView(controls=[...], height=400)

# Avoid - Column for many items
ft.Column(controls=[...])  # Slower for 100+ items
```

### Async Operations

```python
# Good - Async for I/O
async def fetch_data():
    async with aiohttp.ClientSession() as session:
        return await session.get(url)

# Avoid - Blocking I/O
def fetch_data():
    return requests.get(url)  # Blocks UI
```

## Deployment Checklist

Before deploying:
- [ ] Test on all target platforms
- [ ] Remove debug prints
- [ ] Optimize assets (compress images)
- [ ] Set appropriate version numbers
- [ ] Update documentation
- [ ] Test with real users
- [ ] Check accessibility
- [ ] Verify performance

## Resources

- Official Flet documentation: https://docs.flet.dev
- Flet GitHub: https://github.com/flet-dev/flet
- Flet Discord: Community support
- Flet Examples: Code samples and tutorials

## Conclusion

Following these best practices will help you build:
- **Maintainable** applications
- **Performant** user experiences
- **Reliable** software
- **Professional** codebases

Happy coding with Flet!
