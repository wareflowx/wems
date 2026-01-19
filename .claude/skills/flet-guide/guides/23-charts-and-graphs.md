# Charts and Graphs

Flet provides various chart controls for visualizing data, from basic bar charts to complex Plotly integrations.

## BarChart

### Basic Bar Chart

```python
import flet as ft

def main(page: ft.Page):
    chart = ft.BarChart(
        bar_groups=[
            ft.BarChartGroup(
                x=0,
                bars=[
                    ft.BarChartBar(value=30, color=ft.Colors.BLUE),
                ],
            ),
            ft.BarChartGroup(
                x=1,
                bars=[
                    ft.BarChartBar(value=50, color=ft.Colors.GREEN),
                ],
            ),
            ft.BarChartGroup(
                x=2,
                bars=[
                    ft.BarChartBar(value=40, color=ft.Colors.RED),
                ],
            ),
        ],
        bgcolor=ft.Colors.GREY_100,
        width=400,
        height=300,
    )

    page.add(chart)

ft.run(main)
```

### Multiple Bars

```python
def main(page: ft.Page):
    chart = ft.BarChart(
        bar_groups=[
            ft.BarChartGroup(
                x=0,
                bars=[
                    ft.BarChartBar(value=30, color=ft.Colors.BLUE),
                    ft.BarChartBar(value=40, color=ft.Colors.RED),
                ],
            ),
            ft.BarChartGroup(
                x=1,
                bars=[
                    ft.BarChartBar(value=50, color=ft.Colors.BLUE),
                    ft.BarChartBar(value=20, color=ft.Colors.RED),
                ],
            ),
        ],
        width=500,
        height=300,
    )

    page.add(chart)

ft.run(main)
```

## LineChart

### Basic Line Chart

```python
def main(page: ft.Page):
    chart = ft.LineChart(
        data_points=[
            ft.LineChartDataPoint(0, 30),
            ft.LineChartDataPoint(1, 50),
            ft.LineChartDataPoint(2, 40),
            ft.LineChartDataPoint(3, 60),
            ft.LineChartDataPoint(4, 80),
        ],
        width=400,
        height=300,
    )

    page.add(chart)

ft.run(main)
```

### Multiple Lines

```python
def main(page: ft.Page):
    chart = ft.LineChart(
        data_points=[
            ft.LineChartDataPoint(0, 30, color=ft.Colors.BLUE),
            ft.LineChartDataPoint(1, 50, color=ft.Colors.BLUE),
            ft.LineChartDataPoint(2, 40, color=ft.Colors.BLUE),
        ],
        width=400,
        height=300,
    )

    page.add(chart)

ft.run(main)
```

## PieChart

### Basic Pie Chart

```python
def main(page: ft.Page):
    chart = ft.PieChart(
        sections=[
            ft.PieChartSection(value=30, color=ft.Colors.BLUE, radius=10),
            ft.PieChartSection(value=50, color=ft.Colors.GREEN, radius=10),
            ft.PieChartSection(value=40, color=ft.Colors.RED, radius=10),
        ],
        sections_space=0,
        width=400,
        height=400,
    )

    page.add(chart)

ft.run(main)
```

## Plotly Integration

### Use Plotly Charts

```python
def main(page: ft.Page):
    chart = ft.PlotlyChart(
        data={
            "data": [
                {
                    "x": [1, 2, 3, 4],
                    "y": [10, 20, 15, 25],
                    "type": "scatter",
                }
            ]
        },
        width=400,
        height=300,
    )

    page.add(chart)

ft.run(main)
```

## Matplotlib Integration

### Display Matplotlib Charts

```python
import matplotlib.pyplot as plt
import io

def main(page: ft.Page):
    # Create matplotlib figure
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3, 4], [10, 20, 15, 25])

    # Save to bytes
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)

    # Display in Flet
    page.add(
        ft.Image(src_base64=buf.getvalue().decode('latin1'))
    )

ft.run(main)
```

## Best Practices

### 1. Choose Right Chart

```python
# Bar chart - Compare categories
# Line chart - Show trends over time
# Pie chart - Show proportions
```

### 2. Handle Large Data

```python
# Good - Aggregate data
aggregated = aggregate_large_data(raw_data)

# Avoid - Plot thousands of points
chart = ft.LineChart(data_points=thousands_of_points)
```

## Next Steps

1. Integrate web content
2. Deploy to platforms
3. Test applications
4. Build complete apps
