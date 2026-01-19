# Async Applications

Flet supports async/await patterns, enabling efficient concurrent operations without blocking the UI. This is especially important for I/O operations and web apps running in Pyodide.

## Understanding Async in Flet

Flet executes event handlers in separate threads by default. Async handlers allow:
- Non-blocking I/O operations
- Better resource utilization
- Essential for Pyodide (WebAssembly) which doesn't support threading

## Basic Async Pattern

### Async Main Function

```python
import asyncio
import flet as ft

async def main(page: ft.Page):
    page.add(ft.Text("Hello, Async World!"))

ft.run(main)
```

### Async Event Handlers

```python
async def main(page: ft.Page):
    async def handle_click(e):
        # Simulate async operation
        await asyncio.sleep(1)
        print("Button clicked!")

    button = ft.Button("Click me", on_click=handle_click)
    page.add(button)

ft.run(main)
```

## Async Operations

### Async Sleep

```python
async def main(page: ft.Page):
    status = ft.Text("Starting...")

    async def delayed_action(e):
        status.value = "Waiting..."
        page.update()

        await asyncio.sleep(2)

        status.value = "Done!"
        page.update()

    page.add(
        status,
        ft.Button("Start", on_click=delayed_action)
    )

ft.run(main)
```

### HTTP Requests with Async

```python
import aiohttp

async def main(page: ft.Page):
    result_text = ft.Text("Click to fetch data")

    async def fetch_data(e):
        result_text.value = "Loading..."
        page.update()

        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.example.com/data") as response:
                data = await response.json()
                result_text.value = f"Got: {data}"
                page.update()

    page.add(
        result_text,
        ft.Button("Fetch", on_click=fetch_data)
    )

ft.run(main)
```

## Loading States

### Progress Indicator with Async

```python
async def main(page: ft.Page):
    progress = ft.ProgressBar(width=400)
    status = ft.Text("Ready")

    async def long_task(e):
        status.value = "Processing..."
        progress.visible = True
        page.update()

        # Simulate progress
        for i in range(1, 101):
            await asyncio.sleep(0.02)
            progress.value = i / 100
            page.update()

        status.value = "Complete!"
        page.update()

    page.add(
        status,
        progress,
        ft.Button("Start", on_click=long_task)
    )
    progress.visible = False

ft.run(main)
```

## Parallel Async Operations

### Multiple Tasks

```python
async def main(page: ft.Page):
    results = ft.Column()

    async def task(name, duration):
        await asyncio.sleep(duration)
        return f"{name} completed after {duration}s"

    async def run_tasks(e):
        results.controls.clear()
        results.controls.append(ft.Text("Starting tasks..."))
        page.update()

        # Run tasks concurrently
        task1 = asyncio.create_task(task("Task 1", 2))
        task2 = asyncio.create_task(task("Task 2", 1))
        task3 = asyncio.create_task(task("Task 3", 3))

        # Wait for all to complete
        completed = await asyncio.gather(task1, task2, task3)

        results.controls.clear()
        for result in completed:
            results.controls.append(ft.Text(result))
        page.update()

    page.add(
        results,
        ft.Button("Run Tasks", on_click=run_tasks)
    )

ft.run(main)
```

## Async with User Input

### Validating Input Async

```python
async def main(page: ft.Page):
    username = ft.TextField(label="Username")
    status = ft.Text("", color=ft.Colors.GREEN)

    async def validate_username(e):
        if len(username.value) < 3:
            status.value = "Too short"
            status.color = ft.Colors.RED
            page.update()
            return

        status.value = "Checking..."
        status.color = ft.Colors.BLUE
        page.update()

        # Simulate API check
        await asyncio.sleep(1)

        status.value = "Available!"
        status.color = ft.Colors.GREEN
        page.update()

    username.on_change = validate_username

    page.add(username, status)

ft.run(main)
```

## Async File Operations

### Reading Files Async

```python
import aiofiles

async def main(page: ft.Page):
    content = ft.TextField(label="File Content", multiline=True, min_lines=10)

    async def read_file(e):
        async with aiofiles.open("example.txt", "r") as file:
            text = await file.read()
            content.value = text
            page.update()

    page.add(
        content,
        ft.Button("Read File", on_click=read_file)
    )

ft.run(main)
```

## Async Timer

### Countdown Timer

```python
async def main(page: ft.Page):
    remaining = ft.Text("10", size=50)

    async def countdown(e):
        for i in range(10, 0, -1):
            remaining.value = str(i)
            page.update()
            await asyncio.sleep(1)

        remaining.value = "Done!"
        page.update()

    page.add(
        remaining,
        ft.Button("Start", on_click=countdown)
    )

ft.run(main)
```

## Async Polling

### Periodic Updates

```python
async def main(page: ft.Page):
    status = ft.Text("Not running")
    polling = False
    poll_task = None

    async def poll():
        while polling:
            # Simulate API check
            status.value = f"Last update: {asyncio.get_event_loop().time()}"
            page.update()
            await asyncio.sleep(5)

    async def start_polling(e):
        nonlocal polling, poll_task
        if not polling:
            polling = True
            poll_task = asyncio.create_task(poll())

    async def stop_polling(e):
        nonlocal polling
        polling = False
        if poll_task:
            poll_task.cancel()
        status.value = "Stopped"
        page.update()

    page.add(
        status,
        ft.Row([
            ft.Button("Start", on_click=start_polling),
            ft.Button("Stop", on_click=stop_polling),
        ])
    )

ft.run(main)
```

## Error Handling

### Try-Except in Async

```python
async def main(page: ft.Page):
    status = ft.Text("Ready")

    async def risky_operation(e):
        try:
            status.value = "Processing..."
            page.update()

            await asyncio.sleep(1)

            # Simulate error
            raise ValueError("Something went wrong")

        except Exception as ex:
            status.value = f"Error: {str(ex)}"
            status.color = ft.Colors.RED
            page.update()

    page.add(
        status,
        ft.Button("Run", on_click=risky_operation)
    )

ft.run(main)
```

## Cancellation

### Cancel Async Operations

```python
async def main(page: ft.Page):
    status = ft.Text("Ready")
    task = None

    async def long_operation():
        for i in range(10):
            if task and task.cancelled():
                status.value = "Cancelled"
                page.update()
                return

            status.value = f"Step {i + 1}/10"
            page.update()
            await asyncio.sleep(1)

        status.value = "Complete!"
        page.update()

    async def start(e):
        nonlocal task
        task = asyncio.create_task(long_operation())

    async def cancel(e):
        if task:
            task.cancel()

    page.add(
        status,
        ft.Row([
            ft.Button("Start", on_click=start),
            ft.Button("Cancel", on_click=cancel),
        ])
    )

ft.run(main)
```

## Best Practices

### 1. Use Async for I/O Operations

```python
# Good - Async I/O
async def fetch_data():
    async with aiohttp.ClientSession() as session:
        data = await session.get(url)
        return await data.json()

# Avoid - Blocking I/O
def fetch_data():
    response = requests.get(url)  # Blocks
    return response.json()
```

### 2. Update UI in Small Batches

```python
# Good - Batch updates
for item in items:
    process(item)
    if len(processed) % 10 == 0:
        page.update()  # Update every 10 items

# Avoid - Update every iteration
for item in items:
    process(item)
    page.update()  # Too many updates
```

### 3. Handle Exceptions

```python
async def operation():
    try:
        result = await risky_async_call()
        return result
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        raise
```

### 4. Use Timeouts

```python
async def with_timeout():
    try:
        result = await asyncio.wait_for(
            long_operation(),
            timeout=5.0
        )
        return result
    except asyncio.TimeoutError:
        print("Operation timed out")
```

## Next Steps

With async applications covered:

1. Build forms with validation
2. Implement drag and drop
3. Add animations
4. Work with databases
5. Build production apps
