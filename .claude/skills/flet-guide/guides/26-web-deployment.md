# Web Deployment

Deploy Flet applications as web applications for browser access.

## Run as Web App

### Basic Web Mode

```bash
# Run in web browser
flet run --web main.py

# Opens at http://localhost:8550
```

### Custom Port

```bash
# Specify custom port
flet run --web --port 9000 main.py
```

### Host Settings

```python
import flet as ft

def main(page: ft.Page):
    # Web-specific settings
    page.web = True  # Running in web browser
    page.title = "My Web App"
    page.bgcolor = ft.Colors.WHITE

    page.add(ft.Text("Web App"))

ft.run(main, view=ft.AppView.WEB_BROWSER)
```

## Static Website

### Build for Static Hosting

```bash
# Build static website
flet build web

# Output: build/web/
```

### Deploy to Hosting Services

#### Netlify

```bash
# Deploy to Netlify
flet publish web --provider netlify
```

#### Cloudflare Pages

```bash
# Deploy to Cloudflare
flet publish web --provider cloudflare
```

#### GitHub Pages

```bash
# Deploy to GitHub Pages
flet publish web --provider github
```

## Dynamic Website

### Run as Dynamic Web App

```python
import flet as ft

def main(page: ft.Page):
    # Server-side rendering
    page.add(ft.Text("Dynamic Web App"))

ft.run(main, view=ft.AppView.WEB_BROWSER)
```

### Self-Hosted

```bash
# Deploy to own server
flet serve --port 8080 main.py
```

## Web-Specific Features

### URL Parameters

```python
def main(page: ft.Page):
    # Access query parameters
    param1 = page.query.get("param1")
    param2 = page.query.get("param2")

    page.add(ft.Text(f"Params: {param1}, {param2}"))

ft.run(main, view=ft.AppView.WEB_BROWSER)
```

### Deep Linking

```python
def main(page: ft.Page):
    def route_change(route):
        page.content = ft.Text(f"Route: {route}")
        page.update()

    page.on_route_change = route_change

ft.run(main, view=ft.AppView.WEB_BROWSER)
```

## Performance Optimization

### Web Assets

```python
# Configure assets
page.assets_dir = "assets"
page.fonts = {
    "CustomFont": "/fonts/custom.ttf"
}
```

### Lazy Loading

```python
# Load content on demand
def load_view(view_name):
    # Import and load view only when needed
    pass
```

## Best Practices

### 1. Optimize for Web

```python
# Good - Web-friendly
if page.web:
    # Use web-optimized controls
    pass
```

### 2. Handle Browser Compatibility

```python
# Check browser capabilities
if page.platform == "web":
    # Web-specific code
    pass
```

### 3. Use CDN for Assets

```python
# Use CDN for better performance
image_src = "https://cdn.example.com/image.png"
```

## Next Steps

1. Test web applications
2. Monitor performance
3. Optimize load times
4. Deploy to production
