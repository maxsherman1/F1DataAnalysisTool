import pytest
import pandas as pd
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

    static_fig = plot_chart(df, x_col=x_col, y_col=y_col, title=f"Static {plot_kind} plot", plot_type=("static", plot_kind))
    interactive_fig = plot_chart(df, x_col=x_col, y_col=y_col, title=f"Interactive {plot_kind} plot", plot_type=("interactive", plot_kind))

    assert isinstance(static_fig, matplotlib.figure.Figure)
    assert isinstance(interactive_fig, go.Figure)

def test_laps_position_plot():
    df = JolpicaAPI(resource_type="laps", filters={"season": "2023", "round": "18"}).get_cleaned_data()
    lap_data = []
    for i in range(1, int((len(df.columns) - 1) / 3)):
        driver_col = f"Timings.{i}.driverId"
        position_col = f"Timings.{i}.position"
        if driver_col in df.columns and position_col in df.columns:
            for lap in range(len(df)):
                lap_data.append({
                    "lap": df.loc[lap, "number"],
                    "driver": df.loc[lap, driver_col],
                    "position": df.loc[lap, position_col]
                })
    df_clean = pd.DataFrame(lap_data)
    df_clean.sort_values(by=["driver", "lap"], inplace=True)

    static_fig = plot_chart(df_clean, x_col="lap", y_col="position", title="Static Position per Lap", hue="driver", plot_type=("static", "line"), flip_axis=["y"])
    interactive_fig = plot_chart(df_clean, x_col="lap", y_col="position", title="Interactive Position per Lap", hue="driver", plot_type=("interactive", "line"), flip_axis=["y"])

    assert static_fig is not None
    assert interactive_fig is not None
