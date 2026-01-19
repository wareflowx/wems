# Drag and Drop

Drag and drop functionality allows users to move items between containers. Flet provides `Draggable` and `DragTarget` controls for implementing this interaction.

## Basic Drag and Drop

### Simple Draggable Item

```python
import flet as ft

def main(page: ft.Page):
    page.add(
        ft.Column([
            ft.Text("Drag the circle below"),
            ft.Draggable(
                group="color",
                content=ft.Container(
                    width=70,
                    height=70,
                    bgcolor=ft.Colors.BLUE,
                    border_radius=35,
                ),
            )
        ])
    )

ft.run(main)
```

### Basic Drop Target

```python
def main(page: ft.Page):
    def handle_accept(e, id):
        print(f"Dropped item {id}")

    def handle_will_accept(e, id):
        e.control.content.bgcolor = ft.Colors.BLUE_50
        page.update()

    def handle_leave(e):
        e.control.content.bgcolor = ft.Colors.BLUE_100
        page.update()

    drag_target = ft.DragTarget(
        group="color",
        content=ft.Container(
            width=200,
            height=200,
            bgcolor=ft.Colors.BLUE_100,
            border_radius=10,
            alignment=ft.alignment.center,
            content=ft.Text("Drop here", size=20),
        ),
        on_accept=lambda e: handle_accept(e, 1),
        on_will_accept=handle_will_accept,
        on_leave=handle_leave,
    )

    draggable = ft.Draggable(
        group="color",
        content=ft.Container(
            width=70,
            height=70,
            bgcolor=ft.Colors.BLUE,
            border_radius=35,
        ),
    )

    page.add(
        ft.Row([
            draggable,
            drag_target,
        ], spacing=20)
    )

ft.run(main)
```

## Reorderable List

### Basic Reorderable List

```python
def main(page: ft.Page):
    items = [
        ft.Text(f"Item {i}", size=20)
        for i in range(1, 6)
    ]

    page.add(
        ft.Column([
            ft.Text("Drag to reorder", size=20),
            ft.ReorderableListView(
                items=items,
                on_reorder=lambda e: print(f"Reordered: {e.new_index}"),
            )
        ])
    )

ft.run(main)
```

### Custom Reorderable List

```python
def main(page: ft.Page):
    data = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]

    def create_list_tile(text, index):
        return ft.Container(
            ft.ListTile(
                leading=ft.Icon(ft.Icons.DRAG_HANDLE),
                title=ft.Text(text),
            ),
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=5,
            padding=5,
        )

    list_items = [create_list_tile(text, i) for i, text in enumerate(data)]

    page.add(
        ft.ReorderableListView(
            items=list_items,
            on_reorder=lambda e: print(f"Item moved to {e.new_index}"),
        )
    )

ft.run(main)
```

## Drag Between Lists

### Kanban Board Pattern

```python
def main(page: ft.Page):
    def handle_accept_todo(e):
        todo_list.content.controls.append(e.control.content)
        page.update()

    def handle_accept_done(e):
        done_list.content.controls.append(e.control.content)
        page.update()

    todo_list = ft.DragTarget(
        group="task",
        content=ft.Container(
            content=ft.Column([
                ft.Text("To Do", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(
                    ft.Text("Task 1", size=16),
                    bgcolor=ft.Colors.YELLOW_100,
                    padding=10,
                    margin=5,
                ),
            ]),
            bgcolor=ft.Colors.GREY_100,
            padding=10,
            border_radius=10,
            width=250,
        ),
        on_accept=handle_accept_todo,
    )

    done_list = ft.DragTarget(
        group="task",
        content=ft.Container(
            content=ft.Column([
                ft.Text("Done", size=20, weight=ft.FontWeight.BOLD),
            ]),
            bgcolor=ft.Colors.GREY_100,
            padding=10,
            border_radius=10,
            width=250,
        ),
        on_accept=handle_accept_done,
    )

    draggable_task = ft.Draggable(
        group="task",
        content=ft.Container(
            ft.Text("Drag me", size=16),
            bgcolor=ft.Colors.BLUE_100,
            padding=10,
            margin=5,
        ),
    )

    page.add(
        ft.Row([
            todo_list,
            done_list,
        ], spacing=20),
        ft.Divider(height=20),
        draggable_task
    )

ft.run(main)
```

## Color Picker with Drag

```python
def main(page: ft.Page):
    colors = [
        ft.Colors.RED,
        ft.Colors.BLUE,
        ft.Colors.GREEN,
        ft.Colors.YELLOW,
        ft.Colors.PURPLE,
    ]

    color_box = ft.Container(
        ft.Text("Drop color here", size=16),
        width=200,
        height=200,
        bgcolor=ft.Colors.GREY_200,
        border_radius=10,
        alignment=ft.alignment.center,
    )

    def handle_drop_color(e):
        color_box.bgcolor = e.control.content.bgcolor
        color_box.content.value = ""
        page.update()

    drag_target = ft.DragTarget(
        group="color",
        content=color_box,
        on_accept=handle_drop_color,
    )

    color_sources = ft.Row([
        ft.Draggable(
            group="color",
            content=ft.Container(
                width=50,
                height=50,
                bgcolor=color,
                border_radius=25,
            ),
        )
        for color in colors
    ], spacing=10)

    page.add(
        ft.Column([
            drag_target,
            ft.Divider(height=20),
            color_sources,
        ])
    )

ft.run(main)
```

## File Upload with Drag

```python
def main(page: ft.Page):
    upload_zone = ft.DragTarget(
        group="file",
        content=ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.UPLOAD_FILE, size=50, color=ft.Colors.GREY),
                ft.Text("Drag files here", size=16),
            ], alignment=ft.MainAxisAlignment.CENTER),
            width=400,
            height=200,
            bgcolor=ft.Colors.GREY_100,
            border=ft.border.all(2, ft.Colors.BLUE_100),
            border_radius=10,
            alignment=ft.alignment.center,
        ),
    )

    uploaded_files = ft.Column()

    page.add(
        ft.Column([
            upload_zone,
            ft.Divider(height=20),
            ft.Text("Uploaded Files:", size=18, weight=ft.FontWeight.BOLD),
            uploaded_files,
        ])
    )

ft.run(main)
```

## Shopping Cart Pattern

```python
def main(page: ft.Page):
    products = [
        {"name": "Apple", "price": 1.50},
        {"name": "Banana", "price": 0.75},
        {"name": "Orange", "price": 1.25},
    ]

    cart_items = ft.Column()

    cart = ft.DragTarget(
        group="product",
        content=ft.Container(
            content=ft.Column([
                ft.Text("Shopping Cart", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                cart_items,
                ft.Divider(),
                ft.Text("Total: $0.00"),
            ]),
            width=300,
            bgcolor=ft.Colors.GREY_100,
            padding=15,
            border_radius=10,
        ),
        on_accept=lambda e: add_to_cart(e),
    )

    def add_to_cart(e):
        product_name = e.control.content.controls[0].value
        cart_items.controls.append(
            ft.Text(product_name, size=14)
        )
        page.update()

    product_list = ft.Column([
        ft.Draggable(
            group="product",
            content=ft.Container(
                ft.Row([
                    ft.Text(p["name"]),
                    ft.Text(f"${p['price']:.2f}"),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor=ft.Colors.WHITE,
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=5,
            )
        )
        for p in products
    ])

    page.add(
        ft.Row([
            product_list,
            cart,
        ], spacing=20)
    )

ft.run(main)
```

## Best Practices

### 1. Visual Feedback

```python
# Good - Visual feedback on drag
def handle_will_accept(e):
    e.control.content.border = ft.border.all(2, ft.Colors.BLUE)
    page.update()
```

### 2. Use Descriptive Groups

```python
# Good - Descriptive group names
ft.Draggable(group="task", ...)
ft.DragTarget(group="task", ...)

# Avoid - Generic names
ft.Draggable(group="item", ...)
```

### 3. Validate Drops

```python
def handle_will_accept(e):
    # Only accept certain items
    if e.data in allowed_items:
        e.control.content.bgcolor = ft.Colors.GREEN_50
    else:
        e.control.content.bgcolor = ft.Colors.RED_50
```

## Next Steps

With drag and drop covered:

1. Add animations
2. Learn data persistence
3. Work with services
4. Build complex apps
5. Deploy to production
