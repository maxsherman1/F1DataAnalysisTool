import seaborn as sns
import plotly.express as px
import pandas as pd

def format_label(label):
    new_label = ""
    for char in label:
        if char.isupper() and new_label and new_label[-1] != ' ':
            new_label += ' '
        elif char == '.':
            new_label += ' '
            continue
        new_label += char.lower()
    return new_label.capitalize()

def validate_columns(df: pd.DataFrame, x_col: str, y_col: str = None):
    missing_cols = [col for col in [x_col, y_col] if col and col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing column(s) in DataFrame: {', '.join(missing_cols)}")

def preprocess_data(df: pd.DataFrame, x_col: str, y_col: str = None):
    df = df.dropna(subset=[x_col] + ([y_col] if y_col else []))
    if df.empty:
        raise ValueError("DataFrame is empty after removing NaN values.")
    return df

def apply_axis_flip(fig, flip_axis: list, plot_type: str = "static"):

    if flip_axis is None:
        flip_axis=[]

    flip = {
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
        flip[plot_type][axis](fig)

def get_plot_function(plot_type: str, mode="static"):
    plot_mapping = {
        "static": {
            "line": sns.lineplot,
            "bar": sns.barplot,
            "scatter": sns.scatterplot,
            "box": sns.boxplot,
            "hist": sns.histplot,
            "heatmap": sns.heatmap,
            "pie": "pie"  # Placeholder for pie charts in seaborn
        },
        "interactive": {
            "line": px.line,
            "bar": px.bar,
            "scatter": px.scatter,
            "box": px.box
        }
    }
    return plot_mapping[mode].get(plot_type, sns.lineplot if mode == "static" else px.line)  # Default to lineplot