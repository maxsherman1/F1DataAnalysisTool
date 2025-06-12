import f1dataanalysistool.api.data_preprocessing as dp
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import pandas as pd


def format_label(label: str):
    new_label = ""
    for char in label:
        if char.isupper() and new_label and new_label[-1] != ' ':
            new_label += ' '
        elif char == '.':
            new_label += ' '
            continue
        new_label += char.lower()
    return new_label.capitalize()

def apply_axis_flip(fig: go.Figure | plt.Axes, flip_axis: list = None, plot_type: str = "static"):
    if flip_axis is None:
        flip_axis=[]

    flip_methods = {
        "static": {
            "x": lambda f: f.invert_xaxis(),
            "y": lambda f: f.invert_yaxis()
        },
        "interactive": {
            "x": lambda f: f.update_layout(xaxis=dict(autorange="reversed")),
            "y": lambda f: f.update_layout(yaxis=dict(autorange="reversed"))
        }
    }

    for axis in flip_axis:
        flip_methods[plot_type][axis](fig)


def configure_axis_ticks(fig: go.Figure | plt.Axes, df: pd.DataFrame, x_col: str, y_col: str = None):
    def set_ticks(fig, axis: str, col: str):
        min_val, max_val = dp.get_column_min_max(df, col)
        if min_val is not None and max_val is not None:
            tick_vals = list(range(int(min_val), int(max_val) + 1))
            if len(tick_vals) < 30:  # Ensure axis ticks remain readable
                if isinstance(fig, plt.Axes):
                    if axis == "x":
                        fig.set_xticks(tick_vals)
                    elif axis == "y":
                        fig.set_yticks(tick_vals)
                elif isinstance(fig, go.Figure):
                    fig.update_layout(**{f"{axis}axis": dict(tickmode='array', tickvals=tick_vals)})

    if x_col:
        set_ticks(fig, "x", x_col)
    if y_col:
        set_ticks(fig, "y", y_col)