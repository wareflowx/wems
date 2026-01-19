# Pub/Sub Communication

Publish/Subscribe pattern enables communication between different parts of your Flet application without tight coupling.

## Basic Pub/Sub

### Simple Message Passing

```python
import flet as ft

def main(page: ft.Page):
    # Get pubsub client
    pubsub = page.pubsub

    # Subscribe to messages
    def on_message(message):
        print(f"Received: {message}")

    pubsub.subscribe("channel1", on_message)

    # Publish messages
    pubsub.send_all("channel1", "Hello!")

ft.run(main)
```

## Cross-Component Communication

### Communicate Between Components

```python
def main(page: ft.Page):
    pubsub = page.pubsub

    # Component 1 - Sender
    def send_message(e):
        pubsub.send_all("updates", "Button clicked!")

    sender = ft.Button("Send", on_click=send_message)

    # Component 2 - Receiver
    message_display = ft.Text("Waiting...")

    def on_message(message):
        message_display.value = f"Received: {message}"
        page.update()

    pubsub.subscribe("updates", on_message)

    page.add(sender, message_display)

ft.run(main)
```

## Multiple Subscribers

### Broadcast to Multiple Listeners

```python
def main(page: ft.Page):
    pubsub = page.pubsub

    # Multiple subscribers
    def subscriber1(message):
        print(f"Sub1 got: {message}")

    def subscriber2(message):
        print(f"Sub2 got: {message}")

    pubsub.subscribe("events", subscriber1)
    pubsub.subscribe("events", subscriber2)

    # Broadcast
    pubsub.send_all("events", "Hello everyone!")

ft.run(main)
```

## Channel Management

### Subscribe and Unsubscribe

```python
def main(page: ft.Page):
    pubsub = page.pubsub
    subscription_id = None

    def handle_message(message):
        print(f"Message: {message}")

    # Subscribe
    def start_listening(e):
        nonlocal subscription_id
        subscription_id = pubsub.subscribe("channel", handle_message)

    # Unsubscribe
    def stop_listening(e):
        nonlocal subscription_id
        if subscription_id:
            pubsub.unsubscribe("channel", subscription_id)
            subscription_id = None

    page.add(
        ft.Button("Start", on_click=start_listening),
        ft.Button("Stop", on_click=stop_listening)
    )

ft.run(main)
```

## Real-Time Updates

### Update Multiple Components

```python
def main(page: ft.Page):
    pubsub = page.pubsub

    counter1 = ft.Text("0")
    counter2 = ft.Text("0")

    def update_counter1(message):
        counter1.value = str(message)
        page.update()

    def update_counter2(message):
        counter2.value = str(message)
        page.update()

    pubsub.subscribe("counter", update_counter1)
    pubsub.subscribe("counter", update_counter2)

    def increment(e):
        value = int(counter1.value) + 1
        pubsub.send_all("counter", value)

    page.add(
        ft.Row([counter1, counter2]),
        ft.Button("Increment", on_click=increment)
    )

ft.run(main)
```

## Best Practices

### 1. Use Descriptive Channels

```python
# Good
pubsub.send_all("user_updates", data)
pubsub.send_all("status_changes", status)

# Avoid
pubsub.send_all("data", data)
pubsub.send_all("stuff", stuff)
```

### 2. Clean Up Subscriptions

```python
def cleanup():
    for sub_id in subscriptions:
        pubsub.unsubscribe(channel, sub_id)
```

### 3. Handle Messages Safely

```python
def on_message(message):
    try:
        # Process message
        process(message)
    except Exception as e:
        # Handle errors
        print(f"Error: {e}")
```

## Next Steps

1. Add accessibility features
2. Follow best practices
3. Build production apps
4. Deploy applications
