# Building Your First Flet Application

This guide walks through building complete, functional Flet applications step by step. We'll start simple and progressively add features.

## Application 1: Enhanced Counter App

Let's build an enhanced counter application with multiple features.

### Step 1: Basic Counter

```python
import flet as ft

def main(page: ft.Page):
    page.title = "Counter App"
    page.window_width = 400
    page.window_height = 500
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Counter state
    counter_value = 0

    # Display control
    counter_display = ft.Text(
        str(counter_value),
        size=80,
        weight=ft.FontWeight.BOLD
    )

    # Event handlers
    def increment(e):
        nonlocal counter_value
        counter_value += 1
        counter_display.value = str(counter_value)
        page.update()

    def decrement(e):
        nonlocal counter_value
        counter_value -= 1
        counter_display.value = str(counter_value)
        page.update()

    def reset(e):
        nonlocal counter_value
        counter_value = 0
        counter_display.value = str(counter_value)
        page.update()

    # UI
    page.add(
        counter_display,
        ft.Row(
            [
                ft.IconButton(
                    ft.Icons.REMOVE,
                    on_click=decrement,
                    icon_color=ft.Colors.RED
                ),
                ft.IconButton(
                    ft.Icons.REFRESH,
                    on_click=reset,
                    icon_color=ft.Colors.BLUE
                ),
                ft.IconButton(
                    ft.Icons.ADD,
                    on_click=increment,
                    icon_color=ft.Colors.GREEN
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20
        )
    )

ft.run(main)
```

### Step 2: Add History Tracking

```python
import flet as ft
from datetime import datetime

def main(page: ft.Page):
    page.title = "Counter with History"
    page.window_width = 500
    page.window_height = 600
    page.padding = 20

    counter_value = 0
    history = []

    counter_display = ft.Text(
        str(counter_value),
        size=60,
        weight=ft.FontWeight.BOLD
    )

    history_list = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True
    )

    def add_to_history(action, old_value, new_value):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = ft.Container(
            content=ft.Column([
                ft.Text(f"{action}: {old_value} → {new_value}", size=14),
                ft.Text(timestamp, size=10, color=ft.Colors.GREY)
            ]),
            bgcolor=ft.Colors.BLUE_50,
            padding=10,
            border_radius=5
        )
        history_list.controls.append(entry)
        page.update()

    def increment(e):
        nonlocal counter_value
        old_value = counter_value
        counter_value += 1
        counter_display.value = str(counter_value)
        add_to_history("Increment", old_value, counter_value)

    def decrement(e):
        nonlocal counter_value
        old_value = counter_value
        counter_value -= 1
        counter_display.value = str(counter_value)
        add_to_history("Decrement", old_value, counter_value)

    def reset(e):
        nonlocal counter_value
        old_value = counter_value
        counter_value = 0
        counter_display.value = str(counter_value)
        add_to_history("Reset", old_value, counter_value)
        history_list.controls.clear()
        page.update()

    page.add(
        ft.Text("Counter App", size=30, weight=ft.FontWeight.BOLD),
        counter_display,
        ft.Row([
            ft.ElevatedButton("Decrement", on_click=decrement, bgcolor=ft.Colors.RED_100),
            ft.ElevatedButton("Reset", on_click=reset, bgcolor=ft.Colors.BLUE_100),
            ft.ElevatedButton("Increment", on_click=increment, bgcolor=ft.Colors.GREEN_100),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
        ft.Divider(height=30, color=ft.Colors.GREY),
        ft.Text("History", size=20, weight=ft.FontWeight.BOLD),
        ft.Container(
            content=history_list,
            height=300,
            border=ft.border.all(1, ft.Colors.GREY),
            border_radius=5,
            padding=10
        )
    )

ft.run(main)
```

## Application 2: Todo List

A complete todo application with add, delete, and complete functionality.

```python
import flet as ft

def main(page: ft.Page):
    page.title = "Todo App"
    page.window_width = 500
    page.window_height = 700
    page.padding = 30
    page.theme_mode = ft.ThemeMode.LIGHT

    # State
    todos = []

    # Controls
    task_input = ft.TextField(
        hint_text="What needs to be done?",
        expand=True,
        border=ft.border.InputBorder.UNDERLINE
    )

    todo_list = ft.Column(spacing=10)

    def add_todo(e):
        if not task_input.value.strip():
            return

        todo = {
            "task": task_input.value,
            "completed": False
        }
        todos.append(todo)

        def toggle_complete(e):
            todo["completed"] = not todo["completed"]
            checkbox.value = todo["completed"]
            task_text.decoration = (
                ft.TextDecoration.LINE_THROUGH if todo["completed"]
                else ft.TextDecoration.NONE
            )
            task_text.color = (
                ft.Colors.GREY if todo["completed"]
                else ft.Colors.BLACK
            )
            page.update()

        def delete_todo(e):
            todo_row.parent.controls.remove(todo_row)
            todos.remove(todo)
            page.update()

        checkbox = ft.Checkbox(value=False, on_change=toggle_complete)
        task_text = ft.Text(todo["task"], size=16, expand=True)

        todo_row = ft.Container(
            content=ft.Row([
                checkbox,
                task_text,
                ft.IconButton(
                    ft.Icons.DELETE,
                    icon_color=ft.Colors.RED,
                    on_click=delete_todo
                )
            ]),
            bgcolor=ft.Colors.WHITE,
            padding=15,
            border_radius=8,
            shadow=ft.BoxShadow(blur_radius=10, spread_radius=1)
        )

        todo_list.controls.append(todo_row)
        task_input.value = ""
        task_input.focus()
        page.update()

    def handle_submit(e):
        add_todo(e)

    task_input.on_submit = handle_submit

    page.add(
        ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.CHECKLIST, size=40, color=ft.Colors.BLUE),
                ft.Text("My Tasks", size=32, weight=ft.FontWeight.BOLD),
            ]),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            ft.Row([
                task_input,
                ft.FloatingActionButton(
                    ft.Icons.ADD,
                    on_click=add_todo,
                    bgcolor=ft.Colors.BLUE
                )
            ]),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            ft.Text("Active Tasks", size=18, weight=ft.FontWeight.BOLD),
        ]),
        ft.Column(
            [todo_list],
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
    )

ft.run(main)
```

## Application 3: Calculator

A fully functional calculator with a clean interface.

```python
import flet as ft
import math

def main(page: ft.Page):
    page.title = "Calculator"
    page.window_width = 350
    page.window_height = 500
    page.window_resizable = False
    page.padding = 20
    page.bgcolor = ft.Colors.GREY_900

    # State
    current_input = "0"
    previous_input = ""
    operation = None
    reset_input = False

    # Display
    display = ft.Text(
        current_input,
        size=48,
        color=ft.Colors.WHITE,
        text_align=ft.TextAlign.RIGHT,
        weight=ft.FontWeight.LIGHT
    )

    def update_display():
        display.value = current_input
        page.update()

    def number_click(number):
        nonlocal current_input, reset_input
        if reset_input:
            current_input = "0"
            reset_input = False

        if current_input == "0" and number != ".":
            current_input = str(number)
        elif number == "." and "." in current_input:
            return
        else:
            current_input += str(number)
        update_display()

    def operation_click(op):
        nonlocal operation, previous_input, reset_input

        if operation and not reset_input:
            calculate_result()

        previous_input = current_input
        operation = op
        reset_input = True

    def calculate_result():
        nonlocal current_input, previous_input, operation, reset_input

        if not operation or not previous_input:
            return

        try:
            num1 = float(previous_input)
            num2 = float(current_input)

            if operation == "+":
                result = num1 + num2
            elif operation == "-":
                result = num1 - num2
            elif operation == "×":
                result = num1 * num2
            elif operation == "÷":
                if num2 == 0:
                    current_input = "Error"
                    update_display()
                    return
                result = num1 / num2
            else:
                return

            current_input = str(result)
            if current_input.endswith(".0"):
                current_input = current_input[:-2]
            previous_input = ""
            operation = None
            reset_input = True
            update_display()

        except Exception:
            current_input = "Error"
            update_display()

    def clear_all():
        nonlocal current_input, previous_input, operation, reset_input
        current_input = "0"
        previous_input = ""
        operation = None
        reset_input = False
        update_display()

    def clear_entry():
        nonlocal current_input
        current_input = "0"
        update_display()

    def toggle_sign():
        nonlocal current_input
        if current_input != "0":
            if current_input.startswith("-"):
                current_input = current_input[1:]
            else:
                current_input = "-" + current_input
        update_display()

    def percentage():
        nonlocal current_input
        try:
            current_input = str(float(current_input) / 100)
            if current_input.endswith(".0"):
                current_input = current_input[:-2]
            update_display()
        except:
            pass

    # Create button grid
    buttons = [
        ["C", "±", "%", "÷"],
        ["7", "8", "9", "×"],
        ["4", "5", "6", "-"],
        ["1", "2", "3", "+"],
        ["0", ".", "="]
    ]

    button_grid = ft.Column(spacing=10)

    for row in buttons:
        row_controls = []
        for btn_text in row:
            if btn_text == "0":
                btn = ft.Container(
                    content=ft.Text(btn_text, size=24, color=ft.Colors.WHITE),
                    width=160,
                    height=70,
                    bgcolor=ft.Colors.GREY_800,
                    border_radius=35,
                    alignment=ft.alignment.center,
                    on_click=lambda e, n=btn_text: number_click(n)
                )
            elif btn_text == "=":
                btn = ft.Container(
                    content=ft.Text(btn_text, size=24, color=ft.Colors.BLACK),
                    width=160,
                    height=70,
                    bgcolor=ft.Colors.AMBER_400,
                    border_radius=35,
                    alignment=ft.alignment.center,
                    on_click=lambda e: calculate_result()
                )
            elif btn_text in ["÷", "×", "-", "+"]:
                btn = ft.Container(
                    content=ft.Text(btn_text, size=24, color=ft.Colors.WHITE),
                    width=75,
                    height=70,
                    bgcolor=ft.Colors.AMBER_700,
                    border_radius=35,
                    alignment=ft.alignment.center,
                    on_click=lambda e, op=btn_text: operation_click(op)
                )
            elif btn_text == "C":
                btn = ft.Container(
                    content=ft.Text(btn_text, size=24, color=ft.Colors.BLACK),
                    width=75,
                    height=70,
                    bgcolor=ft.Colors.GREY_400,
                    border_radius=35,
                    alignment=ft.alignment.center,
                    on_click=lambda e: clear_all()
                )
            elif btn_text == "±":
                btn = ft.Container(
                    content=ft.Text(btn_text, size=24, color=ft.Colors.BLACK),
                    width=75,
                    height=70,
                    bgcolor=ft.Colors.GREY_400,
                    border_radius=35,
                    alignment=ft.alignment.center,
                    on_click=lambda e: toggle_sign()
                )
            elif btn_text == "%":
                btn = ft.Container(
                    content=ft.Text(btn_text, size=24, color=ft.Colors.BLACK),
                    width=75,
                    height=70,
                    bgcolor=ft.Colors.GREY_400,
                    border_radius=35,
                    alignment=ft.alignment.center,
                    on_click=lambda e: percentage()
                )
            else:
                btn = ft.Container(
                    content=ft.Text(btn_text, size=24, color=ft.Colors.WHITE),
                    width=75,
                    height=70,
                    bgcolor=ft.Colors.GREY_700,
                    border_radius=35,
                    alignment=ft.alignment.center,
                    on_click=lambda e, n=btn_text: number_click(n)
                )
            row_controls.append(btn)

        button_row = ft.Row(row_controls, spacing=10)
        button_grid.controls.append(button_row)

    page.add(
        ft.Container(
            content=display,
            bgcolor=ft.Colors.TRANSPARENT,
            alignment=ft.alignment.center_right,
            padding=20
        ),
        ft.Container(height=20),
        button_grid
    )

ft.run(main)
```

## Application 4: Login Form

A complete login form with validation.

```python
import flet as ft

def main(page: ft.Page):
    page.title = "Login"
    page.window_width = 400
    page.window_height = 500
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = ft.Colors.BLUE_50
    page.padding = 50

    # Form controls
    username = ft.TextField(
        label="Username",
        prefix_icon=ft.Icons.PERSON,
        border=ft.border.InputBorder.OUTLINE,
        border_radius=20,
        width=300
    )

    password = ft.TextField(
        label="Password",
        prefix_icon=ft.Icons.LOCK,
        password=True,
        can_reveal_password=True,
        border=ft.border.InputBorder.OUTLINE,
        border_radius=20,
        width=300
    )

    remember_me = ft.Checkbox(label="Remember me", value=False)
    error_message = ft.Text("", color=ft.Colors.RED)

    def validate_login(e):
        error_message.value = ""

        if not username.value:
            error_message.value = "Please enter your username"
            page.update()
            return

        if len(username.value) < 3:
            error_message.value = "Username must be at least 3 characters"
            page.update()
            return

        if not password.value:
            error_message.value = "Please enter your password"
            page.update()
            return

        if len(password.value) < 6:
            error_message.value = "Password must be at least 6 characters"
            page.update()
            return

        # Simulate successful login
        page.snack_bar = ft.SnackBar(
            ft.Text(f"Welcome, {username.value}!"),
            bgcolor=ft.Colors.GREEN
        )
        page.snack_bar.open = True
        page.update()

    page.add(
        ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(
                        ft.Icons.PERSON,
                        size=50,
                        color=ft.Colors.BLUE
                    ),
                    ft.Text(
                        "Welcome Back",
                        size=30,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE
                    ),
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    username,
                    password,
                    ft.Row([
                        remember_me,
                        ft.TextButton("Forgot Password?", on_click=lambda e: print("Forgot"))
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    error_message,
                    ft.ElevatedButton(
                        "Login",
                        width=300,
                        height=50,
                        bgcolor=ft.Colors.BLUE,
                        color=ft.Colors.WHITE,
                        on_click=validate_login,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=20)
                        )
                    ),
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    ft.Row([
                        ft.Text("Don't have an account?"),
                        ft.TextButton("Sign Up", on_click=lambda e: print("Sign up"))
                    ], alignment=ft.MainAxisAlignment.CENTER)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=40,
                width=400
            ),
            elevation=10
        )
    )

ft.run(main)
```

## Tips for Building Your First Apps

### 1. Start Simple

Begin with the core functionality, then add features incrementally.

### 2. Test Frequently

Run your app often to catch issues early.

```bash
flet run app.py
```

### 3. Use Meaningful Names

Choose descriptive variable and function names.

```python
# Good
submit_button = ft.Button("Submit", on_click=handle_form_submit)

# Bad
b = ft.Button("Submit", on_click=click)
```

### 4. Handle Edge Cases

Consider what happens with empty input, invalid data, etc.

### 5. Provide Feedback

Use snack bars, dialogs, or visual feedback for user actions.

```python
page.snack_bar = ft.SnackBar(
    ft.Text("Operation successful!"),
    bgcolor=ft.Colors.GREEN
)
page.snack_bar.open = True
page.update()
```

### 6. Use Appropriate Controls

Choose the right control for the job:
- `TextField` for single-line input
- `TextField` with `multiline=True` for multi-line text
- `Dropdown` for selecting from options
- `Checkbox` for boolean choices
- `Radio` for mutually exclusive options
- `Switch` for toggle settings

### 7. Layout Responsively

Use `Column`, `Row`, and `ResponsiveRow` to adapt to different screen sizes.

### 8. Keep Functions Focused

Each function should do one thing well.

```python
# Good
def validate_email(email: str) -> bool:
    return "@" in email and "." in email

def validate_password(password: str) -> bool:
    return len(password) >= 8

def handle_submit(e):
    if validate_email(email_field.value):
        # Proceed
        pass

# Avoid
def handle_submit(e):
    # 50 lines of mixed validation and logic
```

## Next Steps

Now that you've built your first applications:

1. Experiment with different controls and layouts
2. Add more features to these examples
3. Learn about navigation for multi-screen apps
4. Implement data persistence
5. Style your apps with theming
6. Deploy your apps to different platforms

The more you practice, the more comfortable you'll become with Flet's patterns and conventions.
