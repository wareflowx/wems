# Layouts and Positioning

Understanding how to position and arrange controls is fundamental to building attractive, functional Flet applications. This guide covers all layout controls and positioning strategies.

## Layout Fundamentals

Flet provides several layout controls that organize child controls in different ways. Choosing the right layout is key to creating responsive, maintainable UIs.

### The Layout Hierarchy

```
Page (root)
└── Container (optional)
    └── Column/Row/Stack
        └── Controls or nested layouts
```

## Column Layout

The `Column` control arranges children vertically from top to bottom.

### Basic Column

```python
import flet as ft

def main(page: ft.Page):
    page.add(
        ft.Column(
            controls=[
                ft.Text("First", size=20),
                ft.Text("Second", size=20),
                ft.Text("Third", size=20),
            ]
        )
    )

ft.run(main)
```

### Column Alignment

```python
def main(page: ft.Page):
    page.add(
        ft.Column(
            controls=[
                ft.Container(
                    ft.Text("Box 1"),
                    width=100,
                    height=50,
                    bgcolor=ft.Colors.BLUE,
                ),
                ft.Container(
                    ft.Text("Box 2"),
                    width=100,
                    height=50,
                    bgcolor=ft.Colors.RED,
                ),
                ft.Container(
                    ft.Text("Box 3"),
                    width=100,
                    height=50,
                    bgcolor=ft.Colors.GREEN,
                ),
            ],
            # Vertical alignment of children within the column
            alignment=ft.MainAxisAlignment.CENTER,  # START, CENTER, END, SPACE_BETWEEN, SPACE_AROUND, SPACE_EVENLY

            # Horizontal alignment of children within the column
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # START, CENTER, END

            # Space between children
            spacing=10,

            # Space between runs (when wrapping)
            run_spacing=20,
        )
    )

ft.run(main)
```

### Column with Wrapping

```python
def main(page: ft.Page):
    page.add(
        ft.Column(
            controls=[
                ft.Container(width=150, height=50, bgcolor=ft.Colors.RED),
                ft.Container(width=150, height=50, bgcolor=ft.Colors.BLUE),
                ft.Container(width=150, height=50, bgcolor=ft.Colors.GREEN),
                ft.Container(width=150, height=50, bgcolor=ft.Colors.YELLOW),
                ft.Container(width=150, height=50, bgcolor=ft.Colors.PURPLE),
            ],
            wrap=True,
            run_alignment=ft.WrapAlignment.CENTER,
            spacing=10,
            run_spacing=10,
        )
    )

ft.run(main)
```

## Row Layout

The `Row` control arranges children horizontally from left to right.

### Basic Row

```python
def main(page: ft.Page):
    page.add(
        ft.Row(
            controls=[
                ft.Text("First", size=20),
                ft.Text("Second", size=20),
                ft.Text("Third", size=20),
            ],
            spacing=20,
        )
    )

ft.run(main)
```

### Row Alignment

```python
def main(page: ft.Page):
    page.add(
        ft.Row(
            controls=[
                ft.Container(
                    ft.Text("Box 1"),
                    width=80,
                    height=80,
                    bgcolor=ft.Colors.BLUE,
                ),
                ft.Container(
                    ft.Text("Box 2"),
                    width=80,
                    height=80,
                    bgcolor=ft.Colors.RED,
                ),
                ft.Container(
                    ft.Text("Box 3"),
                    width=80,
                    height=80,
                    bgcolor=ft.Colors.GREEN,
                ),
            ],
            # Horizontal alignment
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,

            # Vertical alignment
            vertical_alignment=ft.CrossAxisAlignment.CENTER,

            spacing=10,
        )
    )

ft.run(main)
```

### Expanded Children

Use `expand` property to make children fill available space:

```python
def main(page: ft.Page):
    page.add(
        ft.Row(
            controls=[
                ft.Container(
                    ft.Text("Fixed"),
                    width=100,
                    bgcolor=ft.Colors.RED,
                    padding=10
                ),
                ft.Container(
                    ft.Text("Expand 1"),
                    expand=1,  # Takes 1 portion of available space
                    bgcolor=ft.Colors.BLUE,
                    padding=10
                ),
                ft.Container(
                    ft.Text("Expand 2"),
                    expand=2,  # Takes 2 portions (twice as much as expand=1)
                    bgcolor=ft.Colors.GREEN,
                    padding=10
                ),
            ],
        )
    )

ft.run(main)
```

## Container Layout

`Container` is the most versatile layout control. It can contain a single child and provides padding, margin, sizing, and decoration.

### Basic Container

```python
def main(page: ft.Page):
    page.add(
        ft.Container(
            content=ft.Text("Boxed text", size=20),
            width=200,
            height=100,
            bgcolor=ft.Colors.BLUE,
            padding=20,
            margin=10,
        )
    )

ft.run(main)
```

### Container Alignment

```python
def main(page: ft.Page):
    page.add(
        ft.Row(
            [
                # Center alignment
                ft.Container(
                    content=ft.Text("Center", size=16),
                    width=150,
                    height=150,
                    bgcolor=ft.Colors.BLUE_100,
                    alignment=ft.alignment.center,
                ),

                # Top-left alignment
                ft.Container(
                    content=ft.Text("Top Left", size=16),
                    width=150,
                    height=150,
                    bgcolor=ft.Colors.RED_100,
                    alignment=ft.alignment.top_left,
                ),

                # Bottom-right alignment
                ft.Container(
                    content=ft.Text("Bottom Right", size=16),
                    width=150,
                    height=150,
                    bgcolor=ft.Colors.GREEN_100,
                    alignment=ft.alignment.bottom_right,
                ),
            ],
            spacing=20,
        )
    )

ft.run(main)
```

### Container Decoration

```python
def main(page: ft.Page):
    page.add(
        ft.Container(
            content=ft.Text("Styled Container", size=20, color=ft.Colors.WHITE),
            width=300,
            height=150,
            bgcolor=ft.Colors.BLUE,
            padding=20,
            margin=20,
            border_radius=20,
            border=ft.border.all(3, ft.Colors.BLUE_900),
            shadow=ft.BoxShadow(
                blur_radius=20,
                spread_radius=5,
                color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                offset=ft.Offset(0, 5),
            ),
        )
    )

ft.run(main)
```

### Gradient Background

```python
def main(page: ft.Page):
    page.add(
        ft.Container(
            content=ft.Text(
                "Gradient Background",
                size=24,
                color=ft.Colors.WHITE,
                weight=ft.FontWeight.BOLD
            ),
            width=400,
            height=200,
            padding=20,
            alignment=ft.alignment.center,
            # Linear gradient
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[
                    ft.Colors.BLUE,
                    ft.Colors.PURPLE,
                    ft.Colors.PINK,
                ]
            ),
            border_radius=20,
        )
    )

ft.run(main)
```

## Stack Layout

The `Stack` control overlays children on top of each other.

### Basic Stack

```python
def main(page: ft.Page):
    page.add(
        ft.Stack(
            controls=[
                # Bottom layer
                ft.Container(
                    width=300,
                    height=300,
                    bgcolor=ft.Colors.BLUE,
                ),
                # Middle layer
                ft.Container(
                    ft.Text("Middle", size=30),
                    width=200,
                    height=200,
                    bgcolor=ft.Colors.GREEN,
                    alignment=ft.alignment.center,
                ),
                # Top layer
                ft.Container(
                    ft.Text("Top", size=20, color=ft.Colors.WHITE),
                    width=100,
                    height=100,
                    bgcolor=ft.Colors.RED,
                    alignment=ft.alignment.center,
                ),
            ],
            width=300,
            height=300,
        )
    )

ft.run(main)
```

### Positioned Stack

```python
def main(page: ft.Page):
    page.add(
        ft.Stack(
            controls=[
                # Base
                ft.Container(
                    width=400,
                    height=300,
                    bgcolor=ft.Colors.GREY_200,
                ),

                # Positioned elements
                ft.Container(
                    ft.Text("Top Left", color=ft.Colors.WHITE),
                    width=100,
                    height=50,
                    bgcolor=ft.Colors.RED,
                    alignment=ft.alignment.center,
                    left=0,
                    top=0,
                ),
                ft.Container(
                    ft.Text("Top Right", color=ft.Colors.WHITE),
                    width=100,
                    height=50,
                    bgcolor=ft.Colors.BLUE,
                    alignment=ft.alignment.center,
                    right=0,
                    top=0,
                ),
                ft.Container(
                    ft.Text("Bottom Left", color=ft.Colors.WHITE),
                    width=100,
                    height=50,
                    bgcolor=ft.Colors.GREEN,
                    alignment=ft.alignment.center,
                    left=0,
                    bottom=0,
                ),
                ft.Container(
                    ft.Text("Center", color=ft.Colors.WHITE),
                    width=100,
                    height=50,
                    bgcolor=ft.Colors.PURPLE,
                    alignment=ft.alignment.center,
                    left=150,
                    top=125,
                ),
            ],
            width=400,
            height=300,
        )
    )

ft.run(main)
```

## ResponsiveRow

`ResponsiveRow` adapts layout based on screen width using a breakpoint system.

### Breakpoint System

| Breakpoint | Screen Width |
|------------|--------------|
| `xs` | < 576px |
| `sm` | ≥ 576px |
| `md` | ≥ 768px |
| `lg` | ≥ 992px |
| `xl` | ≥ 1200px |
| `xxl` | ≥ 1400px |

### Basic ResponsiveRow

```python
def main(page: ft.Page):
    page.add(
        ft.ResponsiveRow(
            controls=[
                ft.Container(
                    ft.Text("Column 1", color=ft.Colors.WHITE),
                    col={"sm": 12, "md": 6, "lg": 4},
                    bgcolor=ft.Colors.BLUE,
                    padding=20,
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    ft.Text("Column 2", color=ft.Colors.WHITE),
                    col={"sm": 12, "md": 6, "lg": 4},
                    bgcolor=ft.Colors.GREEN,
                    padding=20,
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    ft.Text("Column 3", color=ft.Colors.WHITE),
                    col={"sm": 12, "md": 12, "lg": 4},
                    bgcolor=ft.Colors.RED,
                    padding=20,
                    alignment=ft.alignment.center,
                ),
            ],
        )
    )

ft.run(main)
```

### Advanced Responsive Layout

```python
def main(page: ft.Page):
    page.add(
        ft.ResponsiveRow(
            controls=[
                # Full width on mobile, half on tablet, one-third on desktop
                ft.Container(
                    ft.Text("Card 1", color=ft.Colors.WHITE, size=20),
                    col={"xs": 12, "sm": 6, "md": 4, "lg": 3},
                    bgcolor=ft.Colors.BLUE,
                    padding=30,
                    margin=10,
                    border_radius=10,
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    ft.Text("Card 2", color=ft.Colors.WHITE, size=20),
                    col={"xs": 12, "sm": 6, "md": 4, "lg": 3},
                    bgcolor=ft.Colors.GREEN,
                    padding=30,
                    margin=10,
                    border_radius=10,
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    ft.Text("Card 3", color=ft.Colors.WHITE, size=20),
                    col={"xs": 12, "sm": 6, "md": 4, "lg": 3},
                    bgcolor=ft.Colors.RED,
                    padding=30,
                    margin=10,
                    border_radius=10,
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    ft.Text("Card 4", color=ft.Colors.WHITE, size=20),
                    col={"xs": 12, "sm": 6, "md": 4, "lg": 3},
                    bgcolor=ft.Colors.PURPLE,
                    padding=30,
                    margin=10,
                    border_radius=10,
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    ft.Text("Card 5", color=ft.Colors.WHITE, size=20),
                    col={"xs": 12, "sm": 12, "md": 6, "lg": 6},
                    bgcolor=ft.Colors.ORANGE,
                    padding=30,
                    margin=10,
                    border_radius=10,
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    ft.Text("Card 6", color=ft.Colors.WHITE, size=20),
                    col={"xs": 12, "sm": 12, "md": 6, "lg": 6},
                    bgcolor=ft.Colors.PINK,
                    padding=30,
                    margin=10,
                    border_radius=10,
                    alignment=ft.alignment.center,
                ),
            ],
            run_spacing={"xs": 0, "sm": 10},
        )
    )

ft.run(main)
```

## ListView

`ListView` is a scrollable column optimized for large lists.

### Basic ListView

```python
def main(page: ft.Page):
    items = [ft.Text(f"Item {i}") for i in range(100)]

    page.add(
        ft.ListView(
            controls=items,
            height=400,
            spacing=10,
            padding=20,
        )
    )

ft.run(main)
```

## GridView

`GridView` arranges children in a scrollable grid.

### Basic GridView

```python
def main(page: ft.Page):
    items = []
    for i in range(50):
        items.append(
            ft.Container(
                ft.Text(f"Item {i}", color=ft.Colors.WHITE),
                width=100,
                height=100,
                bgcolor=ft.Colors.BLUE,
                alignment=ft.alignment.center,
                border_radius=10,
            )
        )

    page.add(
        ft.GridView(
            controls=items,
            run_count=5,  # Number of columns
            max_extent=150,  # Maximum item size
            spacing=10,
            run_spacing=10,
            height=500,
        )
    )

ft.run(main)
```

## Padding and Spacing

### Page Padding

```python
def main(page: ft.Page):
    page.padding = 30  # All sides
    # or
    page.padding = ft.padding.all(30)

    # Different padding per side
    page.padding = ft.padding.symmetric(
        horizontal=20,
        vertical=10
    )

    page.add(ft.Text("Padded content"))

ft.run(main)
```

### Control Spacing

```python
def main(page: ft.Page):
    page.add(
        ft.Column(
            [
                ft.Text("First"),
                ft.Text("Second"),
                ft.Text("Third"),
            ],
            spacing=20,  # Space between children
            run_spacing=10,  # Space between runs
        )
    )

ft.run(main)
```

## Sizing Strategies

### Fixed Size

```python
ft.Container(
    content=ft.Text("Fixed"),
    width=200,
    height=100,
)
```

### Expand to Fill

```python
ft.Column(
    [
        ft.Text("Top"),
        ft.Container(
            ft.Text("Expands"),
            expand=True,  # Fills available vertical space
            bgcolor=ft.Colors.BLUE,
        ),
        ft.Text("Bottom"),
    ]
)
```

### Intrinsic Size

Controls size to their content when dimensions aren't specified:

```python
ft.Container(
    ft.Text("Sizes to content"),
    padding=10,
    # No width/height specified - sizes to content
)
```

## Common Layout Patterns

### Center Content

```python
def main(page: ft.Page):
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    page.add(
        ft.Container(
            ft.Text("Centered"),
            width=200,
            height=100,
            bgcolor=ft.Colors.BLUE,
        )
    )

ft.run(main)
```

### Card Layout

```python
def main(page: ft.Page):
    def create_card(title, description):
        return ft.Container(
            content=ft.Column([
                ft.Text(title, size=20, weight=ft.FontWeight.BOLD),
                ft.Text(description, size=14),
            ], spacing=10),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            shadow=ft.BoxShadow(blur_radius=10, spread_radius=1),
            width=300,
        )

    page.add(
        ft.Row(
            [
                create_card("Card 1", "Description 1"),
                create_card("Card 2", "Description 2"),
                create_card("Card 3", "Description 3"),
            ],
            spacing=20,
            wrap=True,
        )
    )

ft.run(main)
```

### Sidebar Layout

```python
def main(page: ft.Page):
    page.add(
        ft.Row(
            [
                # Sidebar
                ft.Container(
                    ft.Column([
                        ft.TextButton("Home", icon=ft.Icons.HOME),
                        ft.TextButton("Profile", icon=ft.Icons.PERSON),
                        ft.TextButton("Settings", icon=ft.Icons.SETTINGS),
                    ], spacing=10),
                    width=200,
                    bgcolor=ft.Colors.GREY_200,
                    padding=20,
                ),
                # Main content
                ft.Container(
                    ft.Text("Main Content", size=30),
                    expand=True,
                    bgcolor=ft.Colors.WHITE,
                    padding=20,
                ),
            ],
            expand=True,
        )
    )

ft.run(main)
```

### App Shell Layout

```python
def main(page: ft.Page):
    def main_layout():
        return ft.Column([
            # App Bar
            ft.Container(
                ft.Text("My App", size=24, weight=ft.FontWeight.BOLD),
                padding=20,
                bgcolor=ft.Colors.BLUE,
            ),
            # Content
            ft.Container(
                ft.Text("Content goes here"),
                expand=True,
                padding=20,
            ),
            # Bottom Navigation
            ft.Container(
                ft.Row([
                    ft.IconButton(ft.Icons.HOME),
                    ft.IconButton(ft.Icons.SEARCH),
                    ft.IconButton(ft.Icons.PERSON),
                ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                padding=20,
                bgcolor=ft.Colors.GREY_200,
            ),
        ], expand=True)

    page.add(main_layout())

ft.run(main)
```

## Best Practices

### 1. Choose the Right Layout

- Use `Column` for vertical stacks
- Use `Row` for horizontal arrangements
- Use `Stack` for overlays
- Use `ResponsiveRow` for adaptive layouts

### 2. Use Spacing Consistently

```python
# Good - consistent spacing
spacing = 10
ft.Column(controls, spacing=spacing)

# Avoid - random spacing
ft.Column(controls, spacing=13)
```

### 3. Set Explicit Sizes When Needed

```python
# Good
ft.Container(width=200, height=100)

# When you need control
ft.Container(expand=True)  # Fills available space
```

### 4. Use Alignment Properties

Prefer alignment properties over manual padding for positioning:

```python
# Good
ft.Container(
    content=ft.Text("Centered"),
    alignment=ft.alignment.center
)

# Avoid
ft.Container(
    content=ft.Text("Centered"),
    padding=ft.padding.symmetric(50, 20)
)
```

### 5. Nest Layouts Wisely

Avoid excessive nesting - 3-4 levels is typically sufficient:

```python
# Good
ft.Column([
    ft.Row([control1, control2]),
    ft.Row([control3, control4]),
])

# Avoid - too deep
ft.Column([
    ft.Container(
        ft.Column([
            ft.Row([
                ft.Container(
                    ft.Row([
                        ft.Text("Deep nesting")
                    ])
                )
            ])
        ])
    )
])
```

## Next Steps

With layouts mastered, you can:

1. Build complex UIs with confidence
2. Create responsive designs
3. Implement common layout patterns
4. Learn about specific controls
5. Handle user interactions
6. Style and theme your applications
