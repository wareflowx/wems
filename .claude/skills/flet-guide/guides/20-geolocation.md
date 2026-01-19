# Geolocation and Maps

Access device location and display interactive maps in Flet applications.

## Geolocator

### Get Current Location

```python
import flet as ft

def main(page: ft.Page):
    geolocator = page.geolocator

    location_text = ft.Text("Location not fetched")

    async def get_location(e):
        try:
            location = await geolocator.get_position()
            location_text.value = (
                f"Lat: {location.latitude}\n"
                f"Long: {location.longitude}\n"
                f"Accuracy: {location.accuracy}m"
            )
            page.update()
        except Exception as ex:
            location_text.value = f"Error: {ex}"
            page.update()

    page.add(
        location_text,
        ft.Button("Get Location", on_click=get_location)
    )

ft.run(main)
```

### Location Stream

```python
def main(page: ft.Page):
    geolocator = page.geolocator

    position_text = ft.Text("Waiting...")

    def on_position_change(position):
        position_text.value = (
            f"Lat: {position.latitude}\n"
            f"Long: {position.longitude}"
        )
        page.update()

    # Start listening for location changes
    geolocator.on_position_change = on_position_change

    page.add(position_text)

ft.run(main)
```

## Map Control

### Display Map

```python
def main(page: ft.Page):
    page.add(
        ft.Map(
            width=400,
            height=300,
            initial_position=ft.MapLatitudeLongitude(
                latitude=48.8566,
                longitude=2.3522,  # Paris
            ),
            zoom=12,
        )
    )

ft.run(main)
```

### Add Markers

```python
def main(page: ft.Page):
    map_control = ft.Map(
        width=400,
        height=300,
        initial_position=ft.MapLatitudeLongitude(48.8566, 2.3522),
        zoom=12,
        layers=[
            ft.MarkerLayer(
                markers=[
                    ft.Marker(
                        position=ft.MapLatitudeLongitude(48.8566, 2.3522),
                        icon=ft.Icon(ft.Icons.LOCATION_ON),
                    )
                ]
            )
        ]
    )

    page.add(map_control)

ft.run(main)
```

## Best Practices

### 1. Handle Permissions

```python
# Request location permissions
async def request_location():
    try:
        position = await geolocator.get_position()
        return position
    except PermissionError:
        # Handle permission denied
        pass
```

### 2. Check Availability

```python
# Check if geolocation is available
if not page.geolocator:
    show_error("Geolocation not available")
```

## Next Steps

1. Work with media files
2. Draw on canvas
3. Add charts
4. Build complete apps
5. Deploy applications
