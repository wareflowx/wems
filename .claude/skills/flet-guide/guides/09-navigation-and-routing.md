# Navigation and Routing

Navigation is essential for multi-page applications. Flet provides a powerful routing system that works across web, desktop, and mobile platforms.

## Understanding Routes

A **route** is the portion of the URL after the `#` symbol in web apps. For example, in `http://localhost:8000/#/settings/profile`, the route is `/settings/profile`.

### Default Route

Every app starts with the default route `/`:

```python
import flet as ft

def main(page: ft.Page):
    page.add(ft.Text(f"Current route: {page.route}"))

ft.run(main, view=ft.AppView.WEB_BROWSER)
```

## Basic Navigation

### Route Change Event

Handle route changes:

```python
import flet as ft

def main(page: ft.Page):
    def route_change(route):
        page.content = ft.Text(f"Route: {page.route}")
        page.update()

    page.on_route_change = route_change
    page.update()

ft.run(main, view=ft.AppView.WEB_BROWSER)
```

### Programmatic Navigation

Change routes programmatically:

```python
def main(page: ft.Page):
    def go_home(e):
        page.go("/")

    def go_settings(e):
        page.go("/settings")

    page.add(
        ft.Row([
            ft.ElevatedButton("Home", on_click=go_home),
            ft.ElevatedButton("Settings", on_click=go_settings),
        ])
    )

ft.run(main, view=ft.AppView.WEB_BROWSER)
```

## View-Based Navigation

Use separate functions for different views:

```python
import flet as ft

def home_view(page):
    return ft.Column([
        ft.Text("Home Page", size=30, weight=ft.FontWeight.BOLD),
        ft.ElevatedButton(
            "Go to Settings",
            on_click=lambda e: page.go("/settings")
        ),
    ])

def settings_view(page):
    return ft.Column([
        ft.Text("Settings Page", size=30, weight=ft.FontWeight.BOLD),
        ft.ElevatedButton(
            "Go to Home",
            on_click=lambda e: page.go("/")
        ),
    ])

def route_change(route):
    if page.route == "/":
        page.content = home_view(page)
    elif page.route == "/settings":
        page.content = settings_view(page)
    page.update()

def main(page: ft.Page):
    page.on_route_change = route_change
    page.go("/")

ft.run(main, view=ft.AppView.WEB_BROWSER)
```

## View Switching Pattern

More elegant view switching:

```python
import flet as ft

class View:
    HOME = "/"
    SETTINGS = "/settings"
    PROFILE = "/profile"
    ABOUT = "/about"

def home_view(page):
    return ft.Column([
        ft.Text("Home", size=30),
        ft.ElevatedButton("Settings", on_click=lambda _: page.go(View.SETTINGS)),
        ft.ElevatedButton("Profile", on_click=lambda _: page.go(View.PROFILE)),
    ], spacing=10)

def settings_view(page):
    return ft.Column([
        ft.Text("Settings", size=30),
        ft.ElevatedButton("Back", on_click=lambda _: page.go(View.HOME)),
    ], spacing=10)

def profile_view(page):
    return ft.Column([
        ft.Text("Profile", size=30),
        ft.ElevatedButton("Back", on_click=lambda _: page.go(View.HOME)),
    ], spacing=10)

def route_change(route):
    views = {
        View.HOME: home_view,
        View.SETTINGS: settings_view,
        View.PROFILE: profile_view,
    }

    page.content = views.get(page.route, home_view)(page)
    page.update()

def main(page: ft.Page):
    page.on_route_change = route_change
    page.go(View.HOME)

ft.run(main, view=ft.AppView.WEB_BROWSER)
```

## Parameterized Routes

Pass parameters in routes:

```python
import flet as ft

def user_view(page, user_id):
    return ft.Column([
        ft.Text(f"User Profile: {user_id}", size=30),
        ft.ElevatedButton("Back", on_click=lambda _: page.go("/")),
    ])

def route_change(route):
    if page.route == "/":
        page.content = ft.Column([
            ft.Text("Users", size=30),
            ft.ElevatedButton("User 1", on_click=lambda _: page.go("/user/1")),
            ft.ElevatedButton("User 2", on_click=lambda _: page.go("/user/2")),
        ])
    elif page.route.startswith("/user/"):
        user_id = page.route.split("/")[-1]
        page.content = user_view(page, user_id)

    page.update()

def main(page: ft.Page):
    page.on_route_change = route_change
    page.go("/")

ft.run(main, view=ft.AppView.WEB_BROWSER)
```

## Navigation with AppBar

Dynamic AppBar based on current route:

```python
import flet as ft

def home_view(page):
    return ft.Column([
        ft.Text("Home Page", size=30),
        ft.ElevatedButton("Settings", on_click=lambda _: page.go("/settings")),
    ])

def settings_view(page):
    return ft.Column([
        ft.Text("Settings Page", size=30),
        ft.ElevatedButton("Home", on_click=lambda _: page.go("/")),
    ])

def update_appbar(page):
    if page.route == "/":
        page.appbar = ft.AppBar(
            title=ft.Text("Home"),
            bgcolor=ft.Colors.BLUE,
        )
    elif page.route == "/settings":
        page.appbar = ft.AppBar(
            title=ft.Text("Settings"),
            bgcolor=ft.Colors.GREEN,
        )
    page.update()

def route_change(route):
    if page.route == "/":
        page.content = home_view(page)
    elif page.route == "/settings":
        page.content = settings_view(page)

    update_appbar(page)
    page.update()

def main(page: ft.Page):
    page.on_route_change = route_change
    page.go("/")

ft.run(main)
```

## Bottom Navigation

Navigation with bottom navigation bar:

```python
import flet as ft

def home_view(page):
    return ft.Column([
        ft.Text("Home", size=30),
        ft.Text("Home content here"),
    ], scroll=ft.ScrollMode.AUTO)

def search_view(page):
    return ft.Column([
        ft.Text("Search", size=30),
        ft.Text("Search content here"),
    ], scroll=ft.ScrollMode.AUTO)

def profile_view(page):
    return ft.Column([
        ft.Text("Profile", size=30),
        ft.Text("Profile content here"),
    ], scroll=ft.ScrollMode.AUTO)

def route_change(route):
    views = {
        "/": (home_view, 0),
        "/search": (search_view, 1),
        "/profile": (profile_view, 2),
    }

    view, index = views.get(page.route, (home_view, 0))
    page.content = view(page)
    page.bottom_navbar.selected_index = index
    page.update()

def main(page: ft.Page):
    page.bottom_navbar = ft.NavigationBar(
        destinations=[
            ft.NavigationDestination(icon=ft.Icons.HOME, label="Home"),
            ft.NavigationDestination(icon=ft.Icons.SEARCH, label="Search"),
            ft.NavigationDestination(icon=ft.Icons.PERSON, label="Profile"),
        ],
        on_change=lambda e: page.go(["/", "/search", "/profile"][e.control.selected_index]),
    )

    page.on_route_change = route_change
    page.go("/")

ft.run(main)
```

## NavigationRail with Views

Side navigation with NavigationRail:

```python
import flet as ft

def dashboard_view(page):
    return ft.Column([
        ft.Text("Dashboard", size=30),
        ft.Text("Dashboard content"),
    ])

def analytics_view(page):
    return ft.Column([
        ft.Text("Analytics", size=30),
        ft.Text("Analytics content"),
    ])

def reports_view(page):
    return ft.Column([
        ft.Text("Reports", size=30),
        ft.Text("Reports content"),
    ])

def route_change(route):
    views = {
        "/dashboard": (dashboard_view, 0),
        "/analytics": (analytics_view, 1),
        "/reports": (reports_view, 2),
    }

    view, index = views.get(page.route, (dashboard_view, 0))
    page.content = view(page)
    page.nav_rail.selected_index = index
    page.update()

def main(page: ft.Page):
    page.nav_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD, label="Dashboard"),
            ft.NavigationRailDestination(icon=ft.Icons.ANALYTICS, label="Analytics"),
            ft.NavigationRailDestination(icon=ft.Icons.ASSIGNMENT, label="Reports"),
        ],
        on_change=lambda e: page.go(["/dashboard", "/analytics", "/reports"][e.control.selected_index]),
    )

    page.add(
        ft.Row([
            page.nav_rail,
            ft.VerticalDivider(width=1),
            ft.Container(expand=True, content=ft.Text("Content")),
        ], expand=True)
    )

    page.on_route_change = route_change
    page.go("/dashboard")

ft.run(main)
```

## Drawer Navigation

Navigation drawer pattern:

```python
import flet as ft

def home_view(page):
    return ft.Column([
        ft.Text("Home", size=30),
        ft.ElevatedButton("Open Drawer", on_click=lambda _: open_drawer()),
    ])

def settings_view(page):
    return ft.Column([
        ft.Text("Settings", size=30),
    ])

def open_drawer():
    page.drawer.open = True
    page.update()

def close_drawer():
    page.drawer.open = False
    page.update()

def route_change(route):
    if page.route == "/":
        page.content = home_view(page)
    elif page.route == "/settings":
        page.content = settings_view(page)
    page.update()

def main(page: ft.Page):
    page.drawer = ft.NavigationDrawer(
        controls=[
            ft.Container(
                ft.Text("My App", size=24, weight=ft.FontWeight.BOLD),
                padding=20,
            ),
            ft.Divider(height=10),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.HOME,
                label="Home",
                selected_icon_content=ft.Icon(ft.Icons.HOME_FILLED),
                on_click=lambda _: (page.go("/"), close_drawer()),
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.SETTINGS,
                label="Settings",
                on_click=lambda _: (page.go("/settings"), close_drawer()),
            ),
        ],
    )

    page.on_route_change = route_change
    page.go("/")

ft.run(main)
```

## Tab-Based Navigation

Using Tabs for navigation:

```python
import flet as ft

def tab_1_content():
    return ft.Column([
        ft.Text("Tab 1 Content", size=30),
        ft.Text("This is the first tab"),
    ])

def tab_2_content():
    return ft.Column([
        ft.Text("Tab 2 Content", size=30),
        ft.Text("This is the second tab"),
    ])

def tab_3_content():
    return ft.Column([
        ft.Text("Tab 3 Content", size=30),
        ft.Text("This is the third tab"),
    ])

def main(page: ft.Page):
    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="Tab 1", content=tab_1_content()),
            ft.Tab(text="Tab 2", content=tab_2_content()),
            ft.Tab(text="Tab 3", content=tab_3_content()),
        ],
    )

    page.add(tabs)

ft.run(main)
```

## View Transitions

Add smooth transitions between views:

```python
import flet as ft

def home_view(page):
    return ft.AnimatedSwitcher(
        content=ft.Column([
            ft.Text("Home", size=30),
            ft.ElevatedButton("Settings", on_click=lambda _: page.go("/settings")),
        ])
    )

def settings_view(page):
    return ft.AnimatedSwitcher(
        content=ft.Column([
            ft.Text("Settings", size=30),
            ft.ElevatedButton("Home", on_click=lambda _: page.go("/")),
        ])
    )

def route_change(route):
    if page.route == "/":
        page.content = home_view(page)
    elif page.route == "/settings":
        page.content = settings_view(page)
    page.update()

def main(page: ft.Page):
    page.on_route_change = route_change
    page.go("/")

ft.run(main)
```

## Browser History

Flet automatically manages browser history:

```python
import flet as ft

def main(page: ft.Page):
    # Enable browser history
    page.title = "Navigation Demo"

    content = ft.Column([
        ft.Text("Navigation Demo", size=30),
        ft.ElevatedButton("Page 1", on_click=lambda _: page.go("/page1")),
        ft.ElevatedButton("Page 2", on_click=lambda _: page.go("/page2")),
    ])

    def route_change(route):
        content.controls.clear()
        content.controls.append(ft.Text(f"Route: {page.route}", size=30))
        content.controls.append(ft.ElevatedButton("Back", on_click=lambda _: page.go_back()))
        page.update()

    page.on_route_change = route_change

ft.run(main, view=ft.AppView.WEB_BROWSER)
```

## Deep Linking

Handle deep links on mobile:

```python
import flet as ft

def handle_initial_route(page):
    # Handle initial route when app opens
    print(f"Initial route: {page.route}")

def main(page: ft.Page):
    def route_change(route):
        if page.route == "/product/123":
            page.content = ft.Text("Product 123")
        elif page.route == "/user/456":
            page.content = ft.Text("User 456")
        else:
            page.content = ft.Text("Home")
        page.update()

    page.on_route_change = route_change
    handle_initial_route(page)

ft.run(main)
```

## Common Patterns

### Protected Routes

Require authentication:

```python
def main(page: ft.Page):
    authenticated = False

    def login_view():
        return ft.Column([
            ft.Text("Please Login", size=30),
            ft.ElevatedButton("Login", on_click=lambda _: do_login()),
        ])

    def dashboard_view():
        return ft.Column([
            ft.Text("Dashboard", size=30),
            ft.Text("Welcome back!"),
            ft.ElevatedButton("Logout", on_click=lambda _: do_logout()),
        ])

    def do_login():
        nonlocal authenticated
        authenticated = True
        page.go("/dashboard")

    def do_logout():
        nonlocal authenticated
        authenticated = False
        page.go("/")

    def route_change(route):
        if not authenticated and page.route != "/":
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

### Loading State During Navigation

```python
def main(page: ft.Page):
    loading = False

    def show_loader():
        nonlocal loading
        loading = True
        page.content = ft.Column([
            ft.ProgressRing(),
            ft.Text("Loading..."),
        ], alignment=ft.MainAxisAlignment.CENTER)
        page.update()

    def hide_loader():
        nonlocal loading
        loading = False

    def route_change(route):
        show_loader()

        # Simulate loading
        import time
        time.sleep(0.5)

        if page.route == "/":
            page.content = ft.Text("Home")
        elif page.route == "/settings":
            page.content = ft.Text("Settings")

        hide_loader()
        page.update()

    page.on_route_change = route_change
    page.go("/")

ft.run(main)
```

## Best Practices

### 1. Use Meaningful Routes

```python
# Good
/page/user/123
/settings/profile

# Avoid
/p1
/s?x=2
```

### 2. Handle 404 Routes

```python
def route_change(route):
    if page.route in views:
        page.content = views[page.route]
    else:
        page.content = ft.Text("Page not found", size=30)
    page.update()
```

### 3. Maintain State Across Routes

Use page properties for shared state:

```python
def main(page: ft.Page):
    page.user_data = {}  # Shared across routes

    def route_change(route):
        # Access page.user_data in any view
        pass
```

### 4. Update AppBar Consistently

```python
def update_appbar(page, title, actions=[]):
    page.appbar = ft.AppBar(
        title=ft.Text(title),
        actions=actions,
    )
    page.update()
```

### 5. Handle Back Button

On mobile, handle back button:

```python
def main(page: ft.Page):
    def on_view_pop(view):
        page.go("/")

    page.on_view_pop = on_view_pop

ft.run(main)
```

## Next Steps

With navigation covered:

1. Learn state management patterns
2. Implement event handling
3. Work with forms and validation
4. Add animations
5. Build complete multi-page applications
