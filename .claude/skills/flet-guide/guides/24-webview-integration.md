# WebView Integration

Embed web content and interact with JavaScript in Flet applications.

## Basic WebView

### Display Web Content

```python
import flet as ft

def main(page: ft.Page):
    webview = ft.WebView(
        url="https://flet.dev",
        width=400,
        height=300,
        on_page_terminate=lambda e: print("Page terminated"),
        on_page_started=lambda e: print("Page started"),
    )

    page.add(webview)

ft.run(main)
```

### HTML Content

```python
def main(page: ft.Page):
    html = """
    <!DOCTYPE html>
    <html>
    <body>
        <h1>Hello from WebView</h1>
        <button onclick="sendMessage()">Click me</button>
        <script>
            function sendMessage() {
                // Communicate with Flet
                window.flutter_inappwebview.callHandler('message', 'Hello from JS');
            }
        </script>
    </body>
    </html>
    """

    webview = ft.WebView(
        html=html,
        width=400,
        height=300,
    )

    page.add(webview)

ft.run(main)
```

## JavaScript Communication

### Call JavaScript from Python

```python
def main(page: ft.Page):
    webview = ft.WebView(
        url="https://example.com",
        width=400,
        height=300,
    )

    def execute_js(e):
        webview.execute_js("alert('Hello from Flet!')")

    page.add(
        webview,
        ft.Button("Execute JS", on_click=execute_js)
    )

ft.run(main)
```

### Handle JavaScript Messages

```python
def main(page: ft.Page):
    webview = ft.WebView(
        url="https://example.com",
        width=400,
        height=300,
        on_web_message=lambda e: print(f"From JS: {e.data}")
    )

    page.add(webview)

ft.run(main)
```

## Best Practices

### 1. Use for External Content

WebView is ideal for:
- Existing web apps
- Third-party embeds
- Complex visualizations

### 2. Handle Loading States

```python
loading = ft.ProgressRing()

def on_page_started(e):
    loading.visible = True
    page.update()

def on_page_terminated(e):
    loading.visible = False
    page.update()
```

## Next Steps

1. Deploy to desktop/mobile
2. Publish web apps
3. Test applications
4. Build complete apps
