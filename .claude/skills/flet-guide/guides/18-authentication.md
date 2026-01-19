# Authentication and Authorization

Implementing secure user authentication in Flet applications.

## Authentication Patterns

### Simple Login Form

```python
import flet as ft

def main(page: ft.Page):
    # Mock user database
    users = {
        "admin": "password123",
        "user": "userpass"
    }

    username = ft.TextField(label="Username", autofocus=True)
    password = ft.TextField(label="Password", password=True, can_reveal_password=True)
    error_text = ft.Text("", color=ft.Colors.RED)

    def handle_login(e):
        if username.value in users and users[username.value] == password.value:
            error_text.value = "Login successful!"
            error_text.color = ft.Colors.GREEN
            page.go("/dashboard")
        else:
            error_text.value = "Invalid username or password"
            error_text.color = ft.Colors.RED
        page.update()

    page.add(
        ft.Column([
            ft.Text("Login", size=30, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20),
            username,
            password,
            error_text,
            ft.ElevatedButton("Login", on_click=handle_login),
        ])
    )

ft.run(main)
```

## Session Management

### Current User Session

```python
def main(page: ft.Page):
    # Store current user in page
    page.current_user = None

    def login_view():
        def handle_login(e):
            # Authenticate user
            page.current_user = {"username": "john", "role": "admin"}
            page.go("/dashboard")

        return ft.Column([
            ft.Text("Login", size=30),
            ft.TextField(label="Username"),
            ft.TextField(label="Password", password=True),
            ft.Button("Login", on_click=handle_login),
        ])

    def dashboard_view():
        def logout(e):
            page.current_user = None
            page.go("/")

        return ft.Column([
            ft.Text(f"Welcome, {page.current_user['username']}", size=30),
            ft.Button("Logout", on_click=logout),
        ])

    def route_change(route):
        if not page.current_user and page.route != "/":
            page.go("/")
            return

        if page.route == "/":
            page.content = login_view()
        elif page.route == "/dashboard":
            page.content = dashboard_view()
        page.update()

    page.on_route_change = route_change
    page.go("/")

ft.run(main)
```

## Protected Routes

### Route Guards

```python
def main(page: ft.Page):
    # Auth state
    page.authenticated = False

    def require_auth(func):
        def wrapper():
            if not page.authenticated:
                page.go("/login")
            else:
                return func()
        return wrapper

    @require_auth
    def dashboard_view():
        return ft.Text("Dashboard - Protected")

    def login_view():
        def login(e):
            page.authenticated = True
            page.go("/dashboard")

        return ft.Column([
            ft.Text("Login"),
            ft.Button("Login", on_click=login),
        ])

    def route_change(route):
        if page.route == "/login":
            page.content = login_view()
        elif page.route == "/dashboard":
            page.content = dashboard_view()
        page.update()

    page.on_route_change = route_change
    page.go("/login")

ft.run(main)
```

## Token-Based Auth

### Store Authentication Token

```python
def main(page: ft.Page):
    # In real app, get token from server
    def authenticate(username, password):
        # Simulate API call
        return "fake-jwt-token-12345"

    def login(e):
        token = authenticate("user", "pass")
        page.client_storage.set("auth_token", token)
        page.client_storage.set("logged_in", True)
        page.go("/dashboard")

    def check_auth():
        return page.client_storage.get("logged_in", False)

    def logout(e):
        page.client_storage.remove("auth_token")
        page.client_storage.remove("logged_in")
        page.go("/login")

    # Use check_auth() in route handlers
    page.add(ft.Text("Token-based auth"))

ft.run(main)
```

## Role-Based Access

### User Roles

```python
def main(page: ft.Page):
    # Mock user with role
    page.user = {
        "username": "admin",
        "role": "administrator"
    }

    def require_role(required_role):
        def decorator(func):
            def wrapper():
                if page.user.get("role") != required_role:
                    return ft.Text("Access Denied", color=ft.Colors.RED, size=20)
                return func()
            return wrapper
        return decorator

    @require_role("administrator")
    def admin_panel():
        return ft.Column([
            ft.Text("Admin Panel", size=24),
            ft.Button("Manage Users"),
        ])

    @require_role("user")
    def user_panel():
        return ft.Column([
            ft.Text("User Panel", size=24),
            ft.Button("View Profile"),
        ])

    # Use admin_panel() or user_panel() based on role
    page.add(admin_panel())

ft.run(main)
```

## OAuth Integration

### OAuth with External Provider

```python
import webbrowser

def main(page: ft.Page):
    def start_oauth(e):
        # In real app, redirect to OAuth provider
        auth_url = "https://example.com/oauth"
        webbrowser.open(auth_url)

        # After redirect, handle callback
        def handle_callback(token):
            page.client_storage.set("oauth_token", token)
            page.go("/dashboard")

    page.add(
        ft.Column([
            ft.Text("Login with OAuth", size=24),
            ft.Button("Login with Google", on_click=start_oauth),
        ])
    )

ft.run(main)
```

## Best Practices

### 1. Never Store Plain Passwords

```python
# Good - Use hash
import hashlib
password_hash = hashlib.sha256(password.encode()).hexdigest()

# Avoid - Plain text
storage.set("password", password)
```

### 2. Use HTTPS in Production

Always use HTTPS for authentication in production apps.

### 3. Implement Logout

```python
def logout(e):
    # Clear all auth data
    page.client_storage.remove("token")
    page.client_storage.remove("user_id")
    page.go("/login")
```

### 4. Token Expiration

```python
def check_token():
    token = page.client_storage.get("auth_token")
    if not token or is_token_expired(token):
        return False
    return True
```

## Next Steps

With authentication covered:

1. Access system services
2. Add geolocation
3. Work with media
4. Draw on canvas
5. Build complete apps
