import pytest
from api.jolpica_api import JolpicaAPI
from visualisation.plot_generator import plot_chart
import matplotlib.figure
import plotly.graph_objs as go

@pytest.mark.parametrize("resource, filters, x_col, y_col, hue, plot_kind", [
    ("pitstops", {"season": "2019", "round": "3"}, "driverId", "duration", None, "box"),
    ("pitstops", {"season": "2019", "round": "3"}, "driverId", "duration", None, "bar"),
    ("pitstops", {"season": "2019", "round": "3"}, "duration", None, None, "box"),
    ("constructorStandings", {"season": "2023"}, "Constructor.name", "points", None, "bar"),
    ("constructorStandings", {"season": "2023"}, "wins", None, None, "pie"),
    ("results", {"season": "2021", "drivers": "max_verstappen"}, "raceName", "Results.points", None, "line"),
    ("constructors", {"season": "2024", "round": "1"}, "nationality", None, None, "pie"),
    ("driverStandings", {"season": "2024"}, "Driver.code", "points", None, "bar"),
    ("driverStandings", {"season": "2024"}, "wins", "points", None, "scatter"),
    ("laps", {"season": "2023", "round": "18"}, "number", "Timings.position", "Timings.driverId", "line")

])
def test_plot_static_and_interactive(resource, filters, x_col, y_col, hue, plot_kind):
    df = JolpicaAPI(resource_type=resource, filters=filters).get_cleaned_data()

    static_fig = plot_chart(df, x_col=x_col, y_col=y_col, title=f"Static {plot_kind} plot", plot_type=("static", plot_kind), saving=True)
    interactive_fig = plot_chart(df, x_col=x_col, y_col=y_col, title=f"Interactive {plot_kind} plot", plot_type=("interactive", plot_kind), saving=True)

    assert isinstance(static_fig, matplotlib.figure.Figure)
    assert isinstance(interactive_fig, go.Figure)

def test_laps_position_plot():
    df = JolpicaAPI(resource_type="laps", filters={"season": "2023", "round": "18"}).get_cleaned_data()

    static_fig = plot_chart(df, x_col="number", y_col="Timings.position", title="Static Position per Lap", hue="Timings.driverId", plot_type=("static", "line"), flip_axis=["y"], saving=True)
    interactive_fig = plot_chart(df, x_col="number", y_col="Timings.position", title="Interactive Position per Lap", hue="Timings.driverId", plot_type=("interactive", "line"), flip_axis=["y"], saving=True)

    assert isinstance(static_fig, matplotlib.figure.Figure)
    assert isinstance(interactive_fig, go.Figure)
