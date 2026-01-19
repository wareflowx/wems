# State Management

State management is about managing data that changes over time and keeping your UI in sync with that data. This guide covers various state management patterns in Flet.

## Understanding State

**State** is any data that can change during your application's lifetime:
- User input
- API responses
- UI state (open/closed, visible/hidden)
- Application data

## Local State with Variables

Simple state stored in local variables:

```python
import flet as ft

def main(page: ft.Page):
    count = 0
    counter_text = ft.Text("0", size=50)

    def increment(e):
        nonlocal count
        count += 1
        counter_text.value = str(count)
        page.update()

    page.add(
        counter_text,
        ft.Button("Increment", on_click=increment)
    )

ft.run(main)
```

## State in Controls

Use controls themselves to store state:

```python
def main(page: ft.Page):
    text_field = ft.TextField(value="Hello")
    display = ft.Text("")

    def update(e):
        display.value = text_field.value
        page.update()

    text_field.on_change = update
    page.add(text_field, display)

ft.run(main)
```

## State Classes

For complex state, create dedicated state classes:

```python
import flet as ft

class CounterState:
    def __init__(self):
        self.count = 0
        self.listeners = []

    def increment(self):
        self.count += 1
        self.notify()

    def decrement(self):
        self.count -= 1
        self.notify()

    def subscribe(self, callback):
        self.listeners.append(callback)

    def notify(self):
        for callback in self.listeners:
            callback(self)

def main(page: ft.Page):
    state = CounterState()
    counter_text = ft.Text("0", size=50)

    def update_ui(state):
        counter_text.value = str(state.count)
        page.update()

    state.subscribe(update_ui)

    page.add(
        counter_text,
        ft.Row([
            ft.Button("Decrement", on_click=lambda e: state.decrement()),
            ft.Button("Increment", on_click=lambda e: state.increment()),
        ])
    )

ft.run(main)
```

## State with Page Properties

Use page properties for shared state:

```python
def main(page: ft.Page):
    # Store state on page
    page.user_data = {
        "username": "",
        "email": "",
    }

    def update_field(field, value):
        page.user_data[field] = value
        print(f"Updated: {page.user_data}")

    username_field = ft.TextField(
        label="Username",
        on_change=lambda e: update_field("username", e.control.value)
    )

    email_field = ft.TextField(
        label="Email",
        on_change=lambda e: update_field("email", e.control.value)
    )

    page.add(username_field, email_field)

ft.run(main)
```

## Observable Pattern

Create observable state that automatically updates UI:

```python
import flet as ft

class Observable:
    def __init__(self, initial_value):
        self._value = initial_value
        self._callbacks = []

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value
        for callback in self._callbacks:
            callback(new_value)

    def bind(self, callback):
        self._callbacks.append(callback)

def main(page: ft.Page):
    counter = Observable(0)
    counter_text = ft.Text("0", size=50)

    # Bind state to UI
    counter.bind(lambda value: setattr(counter_text, 'value', str(value)))
    counter.bind(lambda _: page.update())

    def increment(e):
        counter.value += 1

    page.add(
        counter_text,
        ft.Button("Increment", on_click=increment)
    )

ft.run(main)
```

## State Management with Ref

Use Control refs to access and modify controls:

```python
def main(page: ft.Page):
    name_ref = ft.Ref[ft.TextField]()
    email_ref = ft.Ref[ft.TextField]()

    page.add(
        ft.TextField(ref=name_ref, label="Name"),
        ft.TextField(ref=email_ref, label="Email"),
        ft.Button(
            "Submit",
            on_click=lambda e: print(f"Name: {name_ref.current.value}, Email: {email_ref.current.value}")
        )
    )

ft.run(main)
```

## State Across Routes

Maintain state across navigation:

```python
import flet as ft

class AppState:
    def __init__(self):
        self.user = None
        self.settings = {}

state = AppState()

def home_view(page):
    return ft.Column([
        ft.Text(f"Welcome, {state.user or 'Guest'}"),
        ft.Button("Settings", on_click=lambda e: page.go("/settings"))
    ])

def settings_view(page):
    return ft.Column([
        ft.Text("Settings"),
        ft.Button("Back", on_click=lambda e: page.go("/"))
    ])

def route_change(route):
    if page.route == "/":
        page.content = home_view(page)
    elif page.route == "/settings":
        page.content = settings_view(page)
    page.update()

def main(page: ft.Page):
    page.on_route_change = route_change
    state.user = "John Doe"  # Set initial state
    page.go("/")

ft.run(main)
```

## State with Sessions

Store state per user session:

```python
def main(page: ft.Page):
    # Store in session
    page.session.set("user_id", "12345")
    page.session.set("theme", "dark")

    def get_session_data():
        user_id = page.session.get("user_id")
        theme = page.session.get("theme")
        return f"User: {user_id}, Theme: {theme}"

    page.add(
        ft.Text(get_session_data())
    )

ft.run(main)
```

## Reactive State Builder Pattern

Build UI reactively from state:

```python
import flet as ft

class StateBuilder:
    def __init__(self, page, initial_state):
        self.page = page
        self.state = initial_state
        self.build_ui()

    def set_state(self, **kwargs):
        self.state.update(kwargs)
        self.build_ui()
        self.page.update()

    def build_ui(self):
        # Override in subclass
        pass

class CounterApp(StateBuilder):
    def build_ui(self):
        count = self.state.get("count", 0)

        self.page.content = ft.Column([
            ft.Text(str(count), size=50),
            ft.Button(
                "Increment",
                on_click=lambda e: self.set_state(count=count + 1)
            )
        ])

def main(page: ft.Page):
    CounterApp(page, {"count": 0})

ft.run(main)
```

## State with Data Tables

Managing table state:

```python
def main(page: ft.Page):
    data = [
        {"name": "John", "age": 30},
        {"name": "Jane", "age": 25},
    ]

    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Name")),
            ft.DataColumn(ft.Text("Age")),
        ],
        rows=[]
    )

    def refresh_table():
        data_table.rows.clear()
        for row_data in data:
            data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(row_data["name"])),
                        ft.DataCell(ft.Text(str(row_data["age"]))),
                    ]
                )
            )
        page.update()

    def add_row(e):
        data.append({"name": f"Person {len(data) + 1}", "age": 20})
        refresh_table()

    page.add(
        data_table,
        ft.Button("Add Row", on_click=add_row)
    )
    refresh_table()

ft.run(main)
```

## Form State Management

Managing form state:

```python
class FormState:
    def __init__(self):
        self.data = {}
        self.errors = {}
        self.touched = set()

    def set_value(self, field, value):
        self.data[field] = value
        self.touched.add(field)
        self.validate_field(field)

    def validate_field(self, field):
        if field == "email":
            if "@" not in self.data.get(field, ""):
                self.errors[field] = "Invalid email"
            else:
                self.errors.pop(field, None)

    def is_valid(self):
        return len(self.errors) == 0

def main(page: ft.Page):
    form_state = FormState()

    name_field = ft.TextField(label="Name")
    email_field = ft.TextField(label="Email")
    error_text = ft.Text("", color=ft.Colors.RED)

    def handle_change(e, field):
        form_state.set_value(field, e.control.value)
        if form_state.errors.get(field):
            error_text.value = form_state.errors[field]
            page.update()

    def handle_submit(e):
        if form_state.is_valid():
            print(f"Form data: {form_state.data}")
        else:
            error_text.value = "Please fix errors"
            page.update()

    name_field.on_change = lambda e: handle_change(e, "name")
    email_field.on_change = lambda e: handle_change(e, "email")

    page.add(
        name_field,
        email_field,
        error_text,
        ft.Button("Submit", on_click=handle_submit)
    )

ft.run(main)
```

## Common Patterns

### Singleton State Manager

```python
class StateManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.state = {}
        return cls._instance

    def get(self, key, default=None):
        return self.state.get(key, default)

    def set(self, key, value):
        self.state[key] = value

# Use anywhere
state = StateManager()
state.set("user", "John")
```

### State with Undo/Redo

```python
class HistoryState:
    def __init__(self, initial_value):
        self.value = initial_value
        self.history = [initial_value]
        self.position = 0

    def set(self, value):
        self.value = value
        # Remove future history
        self.history = self.history[:self.position + 1]
        self.history.append(value)
        self.position += 1

    def undo(self):
        if self.position > 0:
            self.position -= 1
            self.value = self.history[self.position]

    def redo(self):
        if self.position < len(self.history) - 1:
            self.position += 1
            self.value = self.history[self.position]
```

## Best Practices

### 1. Keep State Local

```python
# Good - Local state
def create_counter():
    count = 0
    # ... use count here

# Avoid - Global state
count = 0  # Module level
```

### 2. Single Source of Truth

```python
# Good - One source of truth
user = {"name": "John", "email": "john@example.com"}

# Avoid - Duplicated state
user_name = "John"
user_email = "john@example.com"
```

### 3. Immutable Updates

```python
# Good - Create new state
new_state = {**old_state, "count": old_state["count"] + 1}

# Avoid - Mutating directly
old_state["count"] += 1
```

### 4. Separate UI from State

```python
# Good - Separated
class AppState:
    def __init__(self):
        self.data = {}

def build_ui(state):
    # Build UI from state
    pass

# Avoid - Mixed
def build_ui():
    data = {}  # State mixed with UI
```

## Next Steps

With state management covered:

1. Learn about theming and styling
2. Build async applications
3. Work with forms and validation
4. Implement advanced patterns
5. Build complete applications
