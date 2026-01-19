# Animations

Animations bring your Flet apps to life. This guide covers animation techniques and patterns.

## AnimatedSwitcher

Animate transitions between content:

```python
import flet as ft

def main(page: ft.Page):
    text = ft.AnimatedSwitcher(
        content=ft.Text("Hello", size=30),
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=500,
    )

    def toggle_text(e):
        if text.content.value == "Hello":
            text.content = ft.Text("Goodbye", size=30)
        else:
            text.content = ft.Text("Hello", size=30)
        page.update()

    page.add(
        text,
        ft.Button("Toggle", on_click=toggle_text)
    )

ft.run(main)
```

## Animation Control

### Explicit Animations

```python
def main(page: ft.Page):
    container = ft.Container(
        ft.Text("Animated"),
        width=100,
        height=100,
        bgcolor=ft.Colors.BLUE,
        alignment=ft.alignment.center,
    )

    def animate_width(e):
        for width in [100, 200, 300, 200, 100]:
            container.width = width
            page.update()
            time.sleep(0.3)

    page.add(
        container,
        ft.Button("Animate", on_click=animate_width)
    )

ft.run(main)
```

## Implicit Animations

### AnimatedOpacity

```python
def main(page: ft.Page):
    def toggle_opacity(e):
        container.opacity = 0.5 if container.opacity == 1 else 1
        page.update()

    container = ft.Container(
        ft.Text("Fade in/out", size=20),
        width=200,
        height=100,
        bgcolor=ft.Colors.BLUE,
        opacity=1,
        alignment=ft.alignment.center,
        on_click=toggle_opacity,
    )

    page.add(container)

ft.run(main)
```

## Rotation Animation

```python
def main(page: ft.Page):
    icon = ft.Icon(ft.Icons.REFRESH, size=50)

    def rotate(e):
        for i in range(0, 360, 10):
            icon.rotate = ft.Rotate(angle=i)
            page.update()
            time.sleep(0.05)

    page.add(
        icon,
        ft.Button("Rotate", on_click=rotate)
    )

ft.run(main)
```

## Scale Animation

```python
def main(page: ft.Page):
    container = ft.Container(
        ft.Text("Scale me"),
        width=100,
        height=100,
        bgcolor=ft.Colors.RED,
        alignment=ft.alignment.center,
    )

    def pulse(e):
        for scale in [1.0, 1.2, 1.0]:
            container.scale = ft.Scale(scale=scale)
            page.update()
            time.sleep(0.3)

    page.add(
        container,
        ft.Button("Pulse", on_click=pulse)
    )

ft.run(main)
```

## Position Animation

```python
def main(page: ft.Page):
    box = ft.Container(
        width=50,
        height=50,
        bgcolor=ft.Colors.BLUE,
        left=0,
        top=0,
    )

    def move(e):
        for i in range(0, 300, 10):
            box.left = i
            page.update()
            time.sleep(0.02)

    page.add(
        ft.Stack([box], width=400, height=100),
        ft.Button("Move", on_click=move)
    )

ft.run(main)
```

## Loading Animations

### Progress Ring

```python
def main(page: ft.Page):
    progress = ft.ProgressRing(width=50, height=50)

    def simulate_loading(e):
        progress.visible = True
        page.update()

        for i in range(101):
            time.sleep(0.03)
            page.update()

        progress.visible = False
        page.update()

    page.add(
        progress,
        ft.Button("Load", on_click=simulate_loading)
    )
    progress.visible = False

ft.run(main)
```

## Shimmer Effect

```python
def main(page: ft.Page):
    page.add(
        ft.Shimmer(
            ft.Container(
                ft.Column([
                    ft.Text("Loading...", size=20),
                    ft.Text("Please wait"),
                ]),
                width=300,
                height=100,
                bgcolor=ft.Colors.GREY_200,
                padding=20,
            )
        )
    )

ft.run(main)
```

## Animation Patterns

### Fade In Animation

```python
async def fade_in(page, control):
    for opacity in [i / 10 for i in range(11)]:
        control.opacity = opacity
        page.update()
        await asyncio.sleep(0.05)

def main(page: ft.Page):
    text = ft.Text("Fade In", size=30, opacity=0)

    async def start_fade(e):
        await fade_in(page, text)

    page.add(
        text,
        ft.Button("Start", on_click=start_fade)
    )

ft.run(main)
```

### Slide In Animation

```python
def main(page: ft.Page):
    card = ft.Container(
        ft.Text("Slide In"),
        width=200,
        height=100,
        bgcolor=ft.Colors.BLUE,
        alignment=ft.alignment.center,
    )

    def slide_in(e):
        for offset in range(-300, 0, 10):
            card.offset = ft.Offset(offset / 10, 0)
            page.update()
            time.sleep(0.02)

    page.add(
        card,
        ft.Button("Slide In", on_click=slide_in)
    )

ft.run(main)
```

### Bounce Animation

```python
def main(page: ft.Page):
    box = ft.Container(
        ft.Text("Bounce"),
        width=100,
        height=100,
        bgcolor=ft.Colors.GREEN,
        alignment=ft.alignment.center,
    )

    def bounce(e):
        positions = [0, -50, 0, -25, 0]
        for pos in positions:
            box.offset = ft.Offset(0, pos)
            page.update()
            time.sleep(0.1)

    page.add(
        box,
        ft.Button("Bounce", on_click=bounce)
    )

ft.run(main)
```

## Animated Button

```python
def main(page: ft.Page):
    button = ft.ElevatedButton("Hover me")

    def on_hover(e):
        if e.data == "true":
            button.scale = ft.Scale(scale=1.1)
            button.bgcolor = ft.Colors.BLUE_700
        else:
            button.scale = ft.Scale(scale=1.0)
            button.bgcolor = ft.Colors.BLUE
        page.update()

    button.on_hover = on_hover

    page.add(button)

ft.run(main)
```

## Animated List Items

```python
def main(page: ft.Page):
    items = []

    def add_item(e):
        new_item = ft.Container(
            ft.Text(f"Item {len(items) + 1}"),
            width=200,
            bgcolor=ft.Colors.BLUE_100,
            padding=10,
            margin=5,
            opacity=0,
        )

        # Animate in
        items.append(new_item)
        for opacity in [i / 10 for i in range(11)]:
            new_item.opacity = opacity
            page.update()
            time.sleep(0.02)

    page.add(
        ft.Column(items),
        ft.Button("Add Item", on_click=add_item)
    )

ft.run(main)
```

## Best Practices

### 1. Use Appropriate Duration

```python
# Good - Natural timing
transition=ft.AnimatedSwitcherTransition.FADE,
duration=300,  # 300ms is usually good

# Avoid - Too slow
duration=2000  # Feels sluggish
```

### 2. Don't Over-Animate

```python
# Good - Purposeful animations
ft.AnimatedSwitcher(
    transition=ft.AnimatedSwitcherTransition.FADE
)

# Avoid - Distracting
# Everything animated with different transitions
```

### 3. Consider Performance

```python
# Use CSS transforms when possible
container.scale = ft.Scale(scale=1.5)  # Hardware accelerated

# Instead of changing actual size
container.width = 300  # May trigger reflow
```

## Next Steps

With animations covered:

1. Learn data storage
2. Implement authentication
3. Work with services
4. Build complete apps
5. Deploy applications
