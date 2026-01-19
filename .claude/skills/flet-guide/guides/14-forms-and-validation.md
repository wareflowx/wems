# Forms and Validation

Forms are essential for collecting user input. This guide covers building forms with validation, autofill, and error handling.

## Basic Form Structure

```python
import flet as ft

def main(page: ft.Page):
    def handle_submit(e):
        print(f"Name: {name.value}")
        print(f"Email: {email.value}")

    name = ft.TextField(label="Name")
    email = ft.TextField(label="Email")

    page.add(
        ft.Column([
            ft.Text("Contact Form", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20),
            name,
            email,
            ft.ElevatedButton("Submit", on_click=handle_submit),
        ])
    )

ft.run(main)
```

## Form Validation

### Client-Side Validation

```python
def main(page: ft.Page):
    name = ft.TextField(label="Name")
    email = ft.TextField(label="Email")
    password = ft.TextField(label="Password", password=True)
    error_text = ft.Text("", color=ft.Colors.RED)

    def validate_form():
        errors = []

        if not name.value:
            errors.append("Name is required")
        elif len(name.value) < 2:
            errors.append("Name must be at least 2 characters")

        if not email.value:
            errors.append("Email is required")
        elif "@" not in email.value:
            errors.append("Invalid email format")

        if not password.value:
            errors.append("Password is required")
        elif len(password.value) < 6:
            errors.append("Password must be at least 6 characters")

        return errors

    def handle_submit(e):
        errors = validate_form()

        if errors:
            error_text.value = "\n".join(errors)
        else:
            error_text.value = "Form submitted successfully!"
            error_text.color = ft.Colors.GREEN
            # Process form data
            print(f"Form submitted: {name.value}, {email.value}")

        page.update()

    page.add(
        ft.Column([
            ft.Text("Registration", size=24),
            name,
            email,
            password,
            error_text,
            ft.ElevatedButton("Register", on_click=handle_submit),
        ])
    )

ft.run(main)
```

## Real-Time Validation

### Validate on Change

```python
def main(page: ft.Page):
    email = ft.TextField(label="Email")
    email_error = ft.Text("", color=ft.Colors.RED, size=12)

    def validate_email(e):
        if not email.value:
            email_error.value = ""
        elif "@" not in email.value or "." not in email.value:
            email_error.value = "Invalid email format"
        else:
            email_error.value = ""
        page.update()

    email.on_change = validate_email

    page.add(
        ft.Column([
            ft.Text("Newsletter", size=24),
            email,
            email_error,
            ft.ElevatedButton("Subscribe"),
        ])
    )

ft.run(main)
```

## Autofill Groups

Enable browser autofill:

```python
def main(page: ft.Page):
    page.add(
        ft.AutofillGroup(
            ft.Column([
                ft.TextField(
                    label="Name",
                    autofill_hints=[ft.AutofillHint.NAME],
                ),
                ft.TextField(
                    label="Email",
                    autofill_hints=[ft.AutofillHint.EMAIL],
                ),
                ft.TextField(
                    label="Phone",
                    autofill_hints=[ft.AutofillHint.TELEPHONE_NUMBER],
                ),
            ])
        )
    )

ft.run(main)
```

## Form with Multiple Sections

### Sectioned Form

```python
def main(page: ft.Page):
    # Personal Info
    name = ft.TextField(label="Full Name")
    email = ft.TextField(label="Email")

    # Address
    street = ft.TextField(label="Street Address")
    city = ft.TextField(label="City")
    zip_code = ft.TextField(label="ZIP Code")

    def handle_submit(e):
        data = {
            "name": name.value,
            "email": email.value,
            "street": street.value,
            "city": city.value,
            "zip": zip_code.value,
        }
        print(f"Form data: {data}")

    page.add(
        ft.Column([
            ft.Text("Personal Information", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(height=10),
            name,
            email,
            ft.Divider(height=20),
            ft.Text("Address", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(height=10),
            street,
            city,
            zip_code,
            ft.Divider(height=20),
            ft.ElevatedButton("Submit", on_click=handle_submit),
        ])
    )

ft.run(main)
```

## Form State Management

### Form State Class

```python
class FormState:
    def __init__(self):
        self.data = {}
        self.errors = {}
        self.touched = set()

    def set_value(self, field, value):
        self.data[field] = value
        self.touched.add(field)

    def validate(self):
        self.errors.clear()

        if not self.data.get("name"):
            self.errors["name"] = "Name is required"

        if not self.data.get("email"):
            self.errors["email"] = "Email is required"
        elif "@" not in self.data.get("email", ""):
            self.errors["email"] = "Invalid email"

        return len(self.errors) == 0

def main(page: ft.Page):
    state = FormState()

    name = ft.TextField(label="Name")
    email = ft.TextField(label="Email")
    error_text = ft.Text("", color=ft.Colors.RED)

    def update_field(field, value):
        state.set_value(field, value)

        # Clear error for field if present
        if field in state.errors:
            state.errors.pop(field)

        # Update error display
        if state.errors:
            error_text.value = "\n".join(state.errors.values())
        else:
            error_text.value = ""

        page.update()

    def handle_submit(e):
        state.set_value("name", name.value)
        state.set_value("email", email.value)

        if state.validate():
            error_text.value = "Success!"
            error_text.color = ft.Colors.GREEN
            print(f"Form data: {state.data}")
        else:
            error_text.value = "\n".join(state.errors.values())
            error_text.color = ft.Colors.RED

        page.update()

    name.on_change = lambda e: update_field("name", e.control.value)
    email.on_change = lambda e: update_field("email", e.control.value)

    page.add(
        ft.Column([
            ft.Text("Form with State", size=24),
            name,
            email,
            error_text,
            ft.ElevatedButton("Submit", on_click=handle_submit),
        ])
    )

ft.run(main)
```

## Checkbox and Radio Groups

### Multiple Choice Form

```python
def main(page: ft.Page):
    interests = ft.CheckboxGroup(
        label="Interests",
        options=[
            ft.Checkbox("Technology"),
            ft.Checkbox("Sports"),
            ft.Checkbox("Music"),
            ft.Checkbox("Art"),
        ]
    )

    experience = ft.RadioGroup(
        content=ft.Column([
            ft.Radio(value="beginner", label="Beginner"),
            ft.Radio(value="intermediate", label="Intermediate"),
            ft.Radio(value="advanced", label="Advanced"),
        ]),
        value="beginner"
    )

    def handle_submit(e):
        print(f"Interests: {interests.value}")
        print(f"Experience: {experience.value}")

    page.add(
        ft.Column([
            ft.Text("Survey", size=24),
            interests,
            ft.Divider(height=20),
            experience,
            ft.ElevatedButton("Submit", on_click=handle_submit),
        ])
    )

ft.run(main)
```

## Form with File Upload

```python
def main(page: ft.Page):
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)

    selected_file = ft.Text("No file selected")

    def handle_file_pick(result):
        if result.files:
            selected_file.value = f"Selected: {result.files[0].name}"
            page.update()

    file_picker.on_result = handle_file_pick

    page.add(
        ft.Column([
            ft.Text("Upload File", size=24),
            selected_file,
            ft.ElevatedButton(
                "Choose File",
                on_click=lambda _: file_picker.pick_files()
            ),
        ])
    )

ft.run(main)
```

## Reset and Clear

### Form Reset

```python
def main(page: ft.Page):
    name = ft.TextField(label="Name")
    email = ft.TextField(label="Email")
    comments = ft.TextField(label="Comments", multiline=True)

    def reset_form(e):
        name.value = ""
        email.value = ""
        comments.value = ""
        page.update()

    def submit_form(e):
        print(f"Name: {name.value}")
        print(f"Email: {email.value}")
        print(f"Comments: {comments.value}")

    page.add(
        ft.Column([
            ft.Text("Contact Form", size=24),
            name,
            email,
            comments,
            ft.Row([
                ft.ElevatedButton("Submit", on_click=submit_form),
                ft.OutlinedButton("Reset", on_click=reset_form),
            ], spacing=10),
        ])
    )

ft.run(main)
```

## Common Patterns

### Login Form

```python
def main(page: ft.Page):
    username = ft.TextField(label="Username", autofocus=True)
    password = ft.TextField(label="Password", password=True, can_reveal_password=True)
    error_text = ft.Text("", color=ft.Colors.RED)
    remember = ft.Checkbox(label="Remember me")

    def handle_login(e):
        if not username.value or not password.value:
            error_text.value = "Please enter username and password"
            page.update()
            return

        error_text.value = "Login successful!"
        error_text.color = ft.Colors.GREEN
        page.update()

    page.add(
        ft.Column([
            ft.Text("Login", size=30),
            ft.Divider(height=20),
            username,
            password,
            remember,
            error_text,
            ft.ElevatedButton("Login", on_click=handle_login),
        ])
    )

ft.run(main)
```

### Search Form

```python
def main(page: ft.Page):
    search = ft.TextField(label="Search", prefix_icon=ft.Icons.SEARCH, expand=True)
    category = ft.Dropdown(
        label="Category",
        options=[
            ft.dropdown.Option("All"),
            ft.dropdown.Option("Articles"),
            ft.dropdown.Option("Videos"),
            ft.dropdown.Option("Images"),
        ],
        width=200
    )

    def handle_search(e):
        print(f"Searching for '{search.value}' in {category.value}")

    search.on_submit = handle_search

    page.add(
        ft.Row([
            search,
            category,
            ft.FloatingActionButton(ft.Icons.SEARCH, on_click=handle_search),
        ])
    )

ft.run(main)
```

## Best Practices

### 1. Provide Clear Error Messages

```python
# Good - Specific error
"Email must contain '@' symbol"

# Avoid - Generic error
"Invalid input"
```

### 2. Validate on Submit AND Change

```python
# Validate on change for immediate feedback
field.on_change = validate_field

# Also validate on submit for final check
submit_button.on_click = validate_all
```

### 3. Use Appropriate Input Types

```python
ft.TextField(label="Email", keyboard_type=ft.KeyboardType.EMAIL)
ft.TextField(label="Phone", keyboard_type=ft.KeyboardType.PHONE)
ft.TextField(label="Number", keyboard_type=ft.KeyboardType.NUMBER)
```

### 4. Group Related Fields

```python
# Good - Logical grouping
ft.Column([
    ft.Text("Personal Info", size=18, weight=ft.FontWeight.BOLD),
    name_field,
    email_field,
    ft.Divider(),
    ft.Text("Address", size=18, weight=ft.FontWeight.BOLD),
    address_field,
    city_field,
])
```

## Next Steps

With forms covered:

1. Implement drag and drop
2. Add animations
3. Learn data persistence
4. Build complete applications
5. Deploy to production
