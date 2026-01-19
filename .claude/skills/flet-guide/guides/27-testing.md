# Testing Flet Applications

Write tests for your Flet applications to ensure reliability and catch bugs early.

## Unit Testing

### Test with pytest

```python
import pytest
import flet as ft

def test_button_click():
    click_count = [0]

    def on_click(e):
        click_count[0] += 1

    button = ft.Button("Click", on_click=on_click)
    on_click(None)

    assert click_count[0] == 1

def test_text_field():
    field = ft.TextField(value="Hello")
    assert field.value == "Hello"

    field.value = "World"
    assert field.value == "World"
```

## Integration Testing

### Test View Functions

```python
def test_home_view():
    # Create test page
    page = ft.Page()

    # Build view
    content = home_view(page)
    page.add(content)

    # Verify content
    assert len(page.controls) > 0
```

## UI Testing

### Test User Interactions

```python
def test_form_submission():
    page = ft.Page()

    name = ft.TextField(label="Name")
    submit = ft.Button("Submit")

    # Simulate user input
    name.value = "John Doe"

    # Simulate button click
    submit.on_click(None)

    assert name.value == "John Doe"
```

## Test Page Object

### Create Test Page

```python
from flet.testing import PageTest

class TestMyApp(PageTest):
    def test_initial_state(self):
        def main(page):
            page.add(ft.Text("Hello"))

        self.test_page(main)

        # Assertions
        assert any(isinstance(c, ft.Text) for c in self.page.controls)

    def test_button_click(self):
        clicked = [False]

        def main(page):
            button = ft.Button("Click", on_click=lambda e: clicked.__setitem__(0, True))
            page.add(button)

        self.test_page(main)
        self.page.controls[0].on_click(None)

        assert clicked[0]
```

## Best Practices

### 1. Test Critical Paths

```python
# Test important user flows
def test_login_flow():
    # Test login process
    pass

def test_data_submission():
    # Test form submission
    pass
```

### 2. Mock External Dependencies

```python
from unittest.mock import Mock

def test_api_call():
    # Mock API response
    mock_api = Mock()
    mock_api.get_data.return_value = {"result": "success"}

    # Use mock in test
    result = mock_api.get_data()
    assert result["result"] == "success"
```

### 3. Test Edge Cases

```python
def test_empty_input():
    # Test with empty input
    field = ft.TextField(value="")
    assert field.value == ""

def test_max_length():
    # Test max length enforcement
    field = ft.TextField(max_length=10)
    field.value = "Very long text"
    assert len(field.value) <= 10
```

## Next Steps

1. Master Pub/Sub patterns
2. Implement accessibility
3. Follow best practices
4. Build production apps
