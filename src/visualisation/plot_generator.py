import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from api.jolpica_api import JolpicaAPI
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

def apply_axis_flip(flip_axis: str):
    ax = plt.gca()
    if flip_axis in {"y", "both"}:
        ax.invert_yaxis()
    if flip_axis in {"x", "both"}:
        ax.invert_xaxis()

def get_static_plot(plot_type: str):
    plot_mapping = {
        "line": sns.lineplot,
        "bar": sns.barplot,
        "scatter": sns.scatterplot,
        "box": sns.boxplot,
        "hist": sns.histplot,
        "heatmap": sns.heatmap,
        "pie": "pie"
    }
    return plot_mapping.get(plot_type, sns.lineplot)  # Default to lineplot


def plot_static_chart(
        df: pd.DataFrame, x_col: str, y_col: str = None, title: str = "",
        plot_type: str = "line", hue: str = None, figsize: tuple = (10, 5),
        flip_axis: str = None, theme: str = "dark_background", **kwargs
):
    validate_columns(df, x_col, y_col)
    df = preprocess_data(df, x_col, y_col)

    # Set theme and figure size
    plt.style.use(theme)
    plt.figure(figsize=figsize)

    apply_axis_flip(flip_axis)  # Flip axes if needed

    # Special handling for specific plot types
    if plot_type == "heatmap":
        df = df.corr()
    elif plot_type == "hist":
        df = df[x_col]
        y_col = "Frequency"

    static_plot = get_static_plot(plot_type)

    # Handle pie charts separately
    if static_plot == "pie":
        df[x_col].value_counts().plot.pie(autopct='%1.1f%%', **kwargs)
    else:
        static_plot(data=df, x=x_col, y=y_col, hue=hue, **kwargs)

    # Add legend if hue is specified
    if hue:
        plt.legend(title=format_label(hue), bbox_to_anchor=(1, 1), loc="upper left", fontsize=10)

    # Format labels
    x_label = format_label(x_col)
    y_label = format_label(y_col) if y_col else ""

    # Add title and labels
    plt.title(title, fontsize=16, color='white')
    plt.xlabel(x_label, fontsize=12, color='white')
    plt.ylabel(y_label, fontsize=12, color='white')

    # Adjust y-ticks for small numeric ranges
    if y_col and df[y_col].dtype in ['int64', 'float64'] and df[y_col].max() < 30:
        plt.yticks(range(int(df[y_col].min()), int(df[y_col].max()) + 1))

    plt.grid(color="gray", linestyle="--", linewidth=0.5)

    # Rotate x-axis labels if they are too long
    x_labels = [tick.get_text() for tick in plt.gca().get_xticklabels()]
    rotation = 45 if any(len(label) > 5 for label in x_labels) else 0
    plt.xticks(color='white', rotation=rotation, ha='right' if rotation else 'center')

    # Tidy the layout
    plt.tight_layout()
    plt.show()


def plot_interactive_chart(df, x_col, y_col=None, title="", plot_type="line", hue=None, flip_axis=None, **kwargs):
    validate_columns(df, x_col, y_col)
    df = preprocess_data(df, x_col, y_col)

    plot_func = {
        "line": px.line,
        "bar": px.bar,
        "scatter": px.scatter,
        "box": px.box,
        "hist": px.histogram,
        "pie": px.pie,
        "heatmap": px.imshow,
    }

    if plot_type == "pie":
        fig = plot_func[plot_type](df, names=x_col, values=y_col, title=format_label(title), **kwargs)
    elif plot_type == "heatmap":
        fig = plot_func[plot_type](df.corr(), title=format_label(title), color_continuous_scale='coolwarm', **kwargs)
    else:
        fig = plot_func[plot_type](df, x=x_col, y=y_col, color=hue, title=format_label(title), **kwargs)
    fig.update_layout(template="plotly_dark")

    if flip_axis in ["y", "both"]:
        fig.update_yaxes(autorange='reversed')
    if flip_axis in ["x", "both"]:
        fig.update_xaxes(autorange='reversed')

    fig.show()