# Canvas Drawing

Flet's Canvas control allows for custom 2D drawing and graphics.

## Basic Canvas

### Draw Shapes

```python
import flet as ft

def main(page: ft.Page):
    canvas = ft.Canvas(
        width=400,
        height=300,
        content=ft.Stack([
            # Rectangle
            ft.Rect(10, 10, 100, 50, ft.Paint(color=ft.Colors.BLUE)),
            # Circle
            ft.Circle(200, 150, 50, ft.Paint(color=ft.Colors.RED)),
            # Line
            ft.Line(10, 200, 300, 200, ft.Paint(stroke_width=2, color=ft.Colors.GREEN)),
        ])
    )

    page.add(canvas)

ft.run(main)
```

## Drawing Methods

### Draw Path

```python
def main(page: ft.Page):
    path = ft.Path()
    path.move_to(50, 50)
    path.line_to(200, 50)
    path.line_to(200, 150)
    path.close()

    canvas = ft.Canvas(
        width=400,
        height=300,
        content=ft.Stack([
            ft.CanvasPath(
                path,
                ft.Paint(
                    style=ft.PaintingStyle.FILL,
                    color=ft.Colors.BLUE
                )
            )
        ])
    )

    page.add(canvas)

ft.run(main)
```

### Draw Text

```python
def main(page: ft.Page):
    canvas = ft.Canvas(
        width=400,
        height=300,
        content=ft.Stack([
            ft.Text(
                "Hello Canvas",
                x=100,
                y=100,
                paint=ft.Paint(color=ft.Colors.BLACK)
            )
        ])
    )

    page.add(canvas)

ft.run(main)
```

## Interactive Drawing

### Drawing Board

```python
def main(page: ft.Page):
    canvas = ft.Canvas(
        width=400,
        height=300,
        on_click=lambda e: draw(e)
    )

    def draw(e):
        x, y = e.local_x, e.local_y
        # Draw circle at click position
        canvas.content = ft.Stack([
            ft.Circle(x, y, 10, ft.Paint(color=ft.Colors.BLUE))
        ])
        page.update()

    page.add(canvas)

ft.run(main)
```

## Best Practices

### 1. Use Canvas for Custom Graphics

Canvas is ideal for:
- Charts and graphs
- Drawing apps
- Games
- Custom visualizations

### 2. Optimize Drawing

```python
# Good - Batch updates
shapes = []
for item in items:
    shapes.append(create_shape(item))
canvas.content = ft.Stack(shapes)
page.update()  # Single update

# Avoid - Multiple updates
for item in items:
    canvas.content = create_shape(item)
    page.update()  # Update each time
```

## Next Steps

1. Add charts
2. Integrate web content
3. Deploy applications
4. Build complete apps
