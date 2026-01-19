# Advanced UI Controls

This guide covers advanced Flet controls for building complex, feature-rich user interfaces.

## Tabs

Tabs organize content into separate panels.

### Basic Tabs

```python
import flet as ft

def main(page: ft.Page):
    def handle_tab_change(e):
        print(f"Tab changed to: {tabs.selected_index}")

    tabs = ft.Tabs(
        selected_index=0,
        on_change=handle_tab_change,
        tabs=[
            ft.Tab(text="Tab 1", content=ft.Text("Content 1")),
            ft.Tab(text="Tab 2", content=ft.Text("Content 2")),
            ft.Tab(text="Tab 3", content=ft.Text("Content 3")),
        ],
    )

    page.add(tabs)

ft.run(main)
```

### Tabs with Icons

```python
def main(page: ft.Page):
    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(
                tab_content=ft.Row([
                    ft.Icon(ft.Icons.HOME),
                    ft.Text("Home", size=16),
                ], spacing=8),
                content=ft.Text("Home Content")
            ),
            ft.Tab(
                tab_content=ft.Row([
                    ft.Icon(ft.Icons.SEARCH),
                    ft.Text("Search", size=16),
                ], spacing=8),
                content=ft.Text("Search Content")
            ),
            ft.Tab(
                tab_content=ft.Row([
                    ft.Icon(ft.Icons.PERSON),
                    ft.Text("Profile", size=16),
                ], spacing=8),
                content=ft.Text("Profile Content")
            ),
        ],
    )

    page.add(tabs)

ft.run(main)
```

## ListView and Scrollable Content

### Basic ListView

```python
def main(page: ft.Page):
    items = [ft.ListTile(title=ft.Text(f"Item {i}")) for i in range(50)]

    list_view = ft.ListView(
        controls=items,
        spacing=5,
        padding=10,
        height=400,
    )

    page.add(list_view)

ft.run(main)
```

### ListTile with Actions

```python
def main(page: ft.Page):
    def handle_delete(e, item_id):
        print(f"Delete item {item_id}")

    list_view = ft.ListView(
        controls=[
            ft.ListTile(
                leading=ft.Icon(ft.Icons.PERSON),
                title=ft.Text("John Doe"),
                subtitle=ft.Text("Software Engineer"),
                trailing=ft.IconButton(
                    ft.Icons.DELETE,
                    on_click=lambda e, id=1: handle_delete(e, id),
                    icon_color=ft.Colors.RED
                ),
                on_click=lambda e: print("Clicked John"),
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.PERSON),
                title=ft.Text("Jane Smith"),
                subtitle=ft.Text("Product Manager"),
                trailing=ft.IconButton(
                    ft.Icons.DELETE,
                    on_click=lambda e, id=2: handle_delete(e, id),
                    icon_color=ft.Colors.RED
                ),
            ),
        ],
        spacing=5,
        height=300,
    )

    page.add(list_view)

ft.run(main)
```

## DataTable

Display tabular data with sorting and editing capabilities.

### Basic DataTable

```python
def main(page: ft.Page):
    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Name")),
            ft.DataColumn(ft.Text("Age")),
            ft.DataColumn(ft.Text("City")),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("John")),
                    ft.DataCell(ft.Text("30")),
                    ft.DataCell(ft.Text("New York")),
                ],
            ),
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("Jane")),
                    ft.DataCell(ft.Text("25")),
                    ft.DataCell(ft.Text("London")),
                ],
            ),
        ],
        border=ft.border.all(2, ft.Colors.GREY),
        border_radius=10,
    )

    page.add(data_table)

ft.run(main)
```

### Sortable DataTable

```python
def main(page: ft.Page):
    data = [
        {"name": "John", "age": 30, "city": "New York"},
        {"name": "Jane", "age": 25, "city": "London"},
        {"name": "Bob", "age": 35, "city": "Paris"},
    ]

    def sort_data(e, column_index, ascending):
        key = ["name", "age", "city"][column_index]
        data.sort(key=lambda x: x[key], reverse=not ascending)

    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(
                ft.Text("Name"),
                on_sort=lambda e: sort_data(e, 0, True),
            ),
            ft.DataColumn(
                ft.Text("Age"),
                on_sort=lambda e: sort_data(e, 1, True),
            ),
            ft.DataColumn(
                ft.Text("City"),
                on_sort=lambda e: sort_data(e, 2, True),
            ),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(row["name"])),
                    ft.DataCell(ft.Text(str(row["age"]))),
                    ft.DataCell(ft.Text(row["city"])),
                ],
            )
            for row in data
        ],
    )

    page.add(data_table)

ft.run(main)
```

## NavigationRail

Vertical navigation bar for apps with many destinations.

```python
def main(page: ft.Page):
    def handle_destination_change(e):
        content.content = ft.Text(f"Destination: {rail.selected_index}")
        page.update()

    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        on_change=handle_destination_change,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.HOME,
                selected_icon=ft.Icons.HOME_FILLED,
                label="Home",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.FAVORITE_BORDER,
                selected_icon=ft.Icons.FAVORITE,
                label="Favorites",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SETTINGS,
                selected_icon=ft.Icons.SETTINGS,
                label="Settings",
            ),
        ],
    )

    content = ft.Container(
        ft.Text("Home"),
        expand=True,
        padding=20,
    )

    page.add(
        ft.Row([
            rail,
            ft.VerticalDivider(width=1),
            content,
        ], expand=True)
    )

ft.run(main)
```

## NavigationBar

Bottom navigation bar for mobile apps.

```python
def main(page: ft.Page):
    def handle_destination_change(e):
        content.content = ft.Text(f"Destination: {bar.selected_index}")
        page.update()

    bar = ft.NavigationBar(
        destinations=[
            ft.NavigationDestination(
                icon=ft.Icons.HOME,
                label="Home",
            ),
            ft.NavigationDestination(
                icon=ft.Icons.SEARCH,
                label="Search",
            ),
            ft.NavigationDestination(
                icon=ft.Icons.PERSON,
                label="Profile",
            ),
        ],
        on_change=handle_destination_change,
    )

    content = ft.Container(
        ft.Text("Home"),
        expand=True,
        padding=20,
    )

    page.add(
        ft.Column([
            content,
            bar,
        ], expand=True)
    )

ft.run(main)
```

## AppBar

Top app bar with title and actions.

```python
def main(page: ft.Page):
    page.appbar = ft.AppBar(
        title=ft.Text("My App"),
        bgcolor=ft.Colors.BLUE,
        color=ft.Colors.WHITE,
        leading=ft.IconButton(ft.Icons.MENU),
        actions=[
            ft.IconButton(ft.Icons.SEARCH),
            ft.IconButton(ft.Icons.SETTINGS),
            ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(text="Item 1"),
                    ft.PopupMenuItem(text="Item 2"),
                ],
            ),
        ],
    )

    page.add(ft.Text("Content with AppBar"))

ft.run(main)
```

## Card

Material Design card with related content and actions.

```python
def main(page: ft.Page):
    page.add(
        ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.ALBUM),
                        title=ft.Text("Card Title"),
                        subtitle=ft.Text("Card subtitle"),
                    ),
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    ft.Padding(
                        ft.Text("Card content goes here. You can put any controls here."),
                        padding=ft.padding.symmetric(horizontal=15),
                    ),
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    ft.Button("Action", style=ft.ButtonStyle(padding=ft.padding.all(10))),
                ]),
                width=400,
                padding=10,
            ),
            elevation=5,
        )
    )

ft.run(main)
```

## Chip

Compact element representing inputs, attributes, or actions.

```python
def main(page: ft.Page):
    def handle_delete(e, chip):
        chip.visible = False
        page.update()

    chips = ft.Row([
        ft.Chip(
            label=ft.Text("Python"),
            leading=ft.CircleAvatar(content=ft.Text("P"), bgcolor=ft.Colors.BLUE),
            on_delete=lambda e: print("Delete Python"),
        ),
        ft.Chip(
            label=ft.Text("JavaScript"),
            leading=ft.CircleAvatar(content=ft.Text("J"), bgcolor=ft.Colors.YELLOW),
            delete_icon_color=ft.Colors.RED,
        ),
        ft.Chip(
            label=ft.Text("Rust"),
            leading=ft.CircleAvatar(content=ft.Text("R"), bgcolor=ft.Colors.ORANGE),
            delete_icon=ft.Icons.CANCEL,
        ),
    ], spacing=10, wrap=True)

    page.add(chips)

ft.run(main)
```

## Banner

Banner for important announcements.

```python
def main(page: ft.Page):
    def handle_dismiss(e):
        banner.visible = False
        page.update()

    def handle_action(e):
        print("Action clicked")

    banner = ft.Banner(
        bgcolor=ft.Colors.AMBER_100,
        leading=ft.Icon(ft.Icons.WARNING, color=ft.Colors.AMBER),
        content=ft.Text("Important message goes here"),
        actions=[
            ft.TextButton("Learn More", on_click=handle_action),
            ft.TextButton("Dismiss", on_click=handle_dismiss),
        ],
    )

    page.add(
        ft.Column([
            banner,
            ft.Text("Content below banner"),
        ])
    )

ft.run(main)
```

## SegmentedButton

Group related buttons with segmented appearance.

```python
def main(page: ft.Page):
    segmented_button = ft.SegmentedButton(
        segments=[
            ft.ButtonSegment(
                value="day",
                label=ft.Text("Day"),
                icon=ft.Icons.SUNNY,
            ),
            ft.ButtonSegment(
                value="week",
                label=ft.Text("Week"),
                icon=ft.Icons.CALENDAR_VIEW_WEEK,
            ),
            ft.ButtonSegment(
                value="month",
                label=ft.Text("Month"),
                icon=ft.Icons.CALENDAR_MONTH,
            ),
        ],
        selected_value="day",
        on_change=lambda e: print(f"Selected: {e.control.selected_value}"),
    )

    page.add(segmented_button)

ft.run(main)
```

## Expansion Panels

Collapsible panels that expand to reveal content.

### Basic ExpansionPanel

```python
def main(page: ft.Page):
    expansion_panel = ft.ExpansionPanel(
        header=ft.ListTile(
            title=ft.Text("Click to expand"),
        ),
        content=ft.Container(
            content=ft.Text("Hidden content revealed!"),
            padding=10,
        ),
        affinity=ft.PanelAffinity.PLATFORM,
    )

    page.add(
        ft.ExpansionPanelList(
            controls=[expansion_panel],
            expand_icon_color=ft.Colors.BLUE,
        )
    )

ft.run(main)
```

### Multiple ExpansionPanels

```python
def main(page: ft.Page):
    panels = [
        ft.ExpansionPanel(
            header=ft.ListTile(title=ft.Text(f"Panel {i}")),
            content=ft.Container(
                ft.Text(f"Content for panel {i}"),
                padding=10,
            ),
        )
        for i in range(5)
    ]

    page.add(
        ft.ExpansionPanelList(
            controls=panels,
            expanded_header_padding=ft.padding.all(10),
        )
    )

ft.run(main)
```

## BottomSheet

Modal bottom sheet that slides up from bottom.

```python
def main(page: ft.Page):
    def show_bottom_sheet(e):
        page.bottom_sheet = True
        page.bottom_sheet = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Bottom Sheet", size=24, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=20),
                    ft.Text("Content here"),
                    ft.Divider(height=20),
                    ft.ElevatedButton("Close", on_click=close_bottom_sheet),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True),
                padding=20,
            ),
            bgcolor=ft.Colors.WHITE,
            elevation=10,
        )
        page.bottom_sheet.open = True
        page.update()

    def close_bottom_sheet(e):
        page.bottom_sheet.open = False
        page.update()

    page.add(
        ft.ElevatedButton(
            "Show Bottom Sheet",
            on_click=show_bottom_sheet,
        )
    )

ft.run(main)
```

## NavigationDrawer

Side drawer for navigation destinations.

```python
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
                selected_icon=ft.Icons.HOME_FILLED,
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.FAVORITE_BORDER,
                label="Favorites",
                selected_icon_content=ft.Icon(ft.Icons.FAVORITE),
            ),
            ft.Divider(height=10),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.SETTINGS,
                label="Settings",
            ),
        ],
    )

    def open_drawer(e):
        page.drawer.open = True
        page.update()

    page.add(
        ft.ElevatedButton(
            "Open Drawer",
            on_click=open_drawer,
        )
    )

ft.run(main)
```

## Chip (Filter Chips)

```python
def main(page: ft.Page):
    selected_filters = set()

    def toggle_filter(e, filter_name):
        if filter_name in selected_filters:
            selected_filters.remove(filter_name)
        else:
            selected_filters.add(filter_name)

        # Update chip appearance
        for chip in filter_chip.controls:
            if chip.label.value == filter_name:
                chip.selected = not chip.selected

        print(f"Selected: {selected_filters}")
        page.update()

    filter_chip = ft.Row([
        ft.FilterChip(
            label=ft.Text(filter_name),
            selected=filter_name in selected_filters,
            on_select=lambda e, f=filter_name: toggle_filter(e, f),
            check_color=ft.Colors.BLUE,
        )
        for filter_name in ["Python", "JavaScript", "Rust", "Go"]
    ], spacing=10, wrap=True)

    page.add(
        ft.Column([
            ft.Text("Filters:", size=20, weight=ft.FontWeight.BOLD),
            filter_chip,
        ], spacing=10)
    )

ft.run(main)
```

## Common Patterns

### Master-Detail View

```python
def main(page: ft.Page):
    def handle_item_select(e):
        content.content = ft.Column([
            ft.Text(f"Item: {e.control.title.value}", size=24),
            ft.Text(f"Details for {e.control.title.value}"),
        ])
        page.update()

    master_list = ft.ListView(
        controls=[
            ft.ListTile(
                title=ft.Text(f"Item {i}"),
                on_click=handle_item_select,
            )
            for i in range(20)
        ],
        height=400,
        spacing=5,
    )

    content = ft.Container(
        ft.Text("Select an item"),
        expand=True,
        bgcolor=ft.Colors.GREY_100,
        padding=20,
    )

    page.add(
        ft.Row([
            ft.Container(master_list, width=300),
            ft.VerticalDivider(width=1),
            content,
        ], expand=True)
    )

ft.run(main)
```

### Grid of Cards

```python
def main(page: ft.Page):
    cards = ft.GridView(
        controls=[
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text(f"Card {i}", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Description {i}"),
                    ], spacing=10),
                    padding=20,
                ),
                elevation=5,
            )
            for i in range(12)
        ],
        run_count=3,
        max_extent=250,
        spacing=20,
        run_spacing=20,
    )

    page.add(cards)

ft.run(main)
```

## Best Practices

### 1. Choose Appropriate Controls

- Use `Tabs` for switching between related views
- Use `NavigationBar` for 3-5 top-level destinations
- Use `NavigationRail` for 5+ destinations
- Use `DataTable` for tabular data
- Use `ListView` for scrolling lists

### 2. Maintain Consistent Spacing

```python
# Good
spacing = 10
ft.ListView(controls, spacing=spacing, padding=spacing)

# Avoid
ft.ListView(controls, spacing=13, padding=27)
```

### 3. Provide Visual Hierarchy

```python
# Good - Clear hierarchy
ft.Column([
    ft.Text("Title", size=30, weight=ft.FontWeight.BOLD),
    ft.Text("Subtitle", size=18, color=ft.Colors.GREY),
    ft.Text("Body", size=14),
])
```

### 4. Use Icons Meaningfully

Icons should aid understanding:

```python
# Good
ft.NavigationRailDestination(
    icon=ft.Icons.HOME,
    label="Home",
)
```

### 5. Optimize Performance with ListView

For large lists, always use `ListView` instead of `Column`:

```python
# Good - Efficient
ft.ListView(controls=[...], height=400)

# Avoid - Inefficient for many items
ft.Column(controls=[...])
```

## Next Steps

With advanced controls mastered:

1. Learn about dialogs and popups
2. Implement navigation patterns
3. Create responsive layouts
4. Handle complex user interactions
5. Style with theming
