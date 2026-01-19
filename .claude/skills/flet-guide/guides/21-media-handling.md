# Media Handling

Work with audio, video, images, and animations in Flet applications.

## Audio

### Play Audio

```python
import flet as ft

def main(page: ft.Page):
    audio = ft.Audio(
        src="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
        autoplay=False,
        volume=1.0,
        balance=0.0,
    )

    page.add(
        audio,
        ft.Row([
            ft.IconButton(ft.Icons.PLAY_ARROW, on_click=lambda e: audio.play()),
            ft.IconButton(ft.Icons.PAUSE, on_click=lambda e: audio.pause()),
            ft.IconButton(ft.Icons.STOP, on_click=lambda e: audio.stop()),
        ])
    )

ft.run(main)
```

### Audio Recorder

```python
def main(page: ft.Page):
    recorder = ft.AudioRecorder()

    def start_recording(e):
        recorder.start_recording()

    def stop_recording(e):
        recorder.stop_recording()
        # Get recording
        recording = recorder.get_recording()

    page.add(
        ft.Button("Record", on_click=start_recording),
        ft.Button("Stop", on_click=stop_recording)
    )

ft.run(main)
```

## Video

### Play Video

```python
def main(page: ft.Page):
    video = ft.Video(
        playlist=[ft.VideoMedia(
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
        )],
        autoplay=False,
        show_controls=True,
        width=400,
        height=300,
    )

    page.add(video)

ft.run(main)
```

### Video Controls

```python
def main(page: ft.Page):
    video = ft.Video(
        playlist=[ft.VideoMedia("video.mp4")],
        width=400,
        height=300,
    )

    page.add(
        video,
        ft.Row([
            ft.Button("Play", on_click=lambda e: video.play()),
            ft.Button("Pause", on_click=lambda e: video.pause()),
            ft.Slider(
                min_value=0,
                max_value=1,
                value=0.5,
                on_change=lambda e: setattr(video, 'playback_rate', e.control.value)
            ),
        ])
    )

ft.run(main)
```

## Images

### Display Image

```python
def main(page: ft.Page):
    page.add(
        ft.Image(
            src="/path/to/image.png",
            width=300,
            height=200,
            fit=ft.ImageFit.CONTAIN,
        )
    )

ft.run(main)
```

### Network Images

```python
def main(page: ft.Page):
    page.add(
        ft.Image(
            src="https://picsum.photos/300/200",
            width=300,
            height=200,
            border_radius=10,
        )
    )

ft.run(main)
```

## Lottie Animations

### Display Lottie

```python
def main(page: ft.Page):
    page.add(
        ft.Lottie(
            src="https://assets2.lottiefiles.com/packages/lf20_u4yrau.json",
            width=300,
            height=300,
            repeat=True,
            autoplay=True,
        )
    )

ft.run(main)
```

## Best Practices

### 1. Optimize Media

```python
# Good - Use appropriate sizes
ft.Image(src="image.jpg", width=300)

# Avoid - Full resolution when not needed
ft.Image(src="huge_4k_image.jpg")
```

### 2. Handle Loading

```python
# Show loading indicator
loading = ft.ProgressRing()
image = ft.Image(src="...", on_load=lambda e: set_loaded())
```

## Next Steps

1. Draw on canvas
2. Add charts
3. Build complete apps
4. Deploy applications
