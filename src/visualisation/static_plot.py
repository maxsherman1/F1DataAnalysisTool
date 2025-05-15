from visualisation.plot_utils import format_label, apply_axis_flip, configure_axis_ticks
from enumeration.plot_types import PlotMode, PlotType, PlotFunction
import matplotlib.pyplot as plt
import pandas as pd

def plot_static_chart(
        df: pd.DataFrame, x_col: str, y_col: str = None, title: str = "",
        plot_type: str = "line", hue: str = None, figsize: tuple[float, float] = (10, 5),
        flip_axis: list = None, theme: str = "default", **kwargs
):
    # Set theme and figure size
    plt.style.use(theme)
    fig, ax = plt.subplots(figsize=figsize)

    apply_axis_flip(ax, flip_axis, plot_type="static")  # Flip axes if needed

    # Special handling for specific plot types
    if plot_type == "heatmap":
        df = df.corr()
    elif plot_type == "hist":
        df = df[x_col]
        y_col = "Frequency"


    plot_function = PlotFunction.get_plot_function(plot_type=PlotType(plot_type), mode=PlotMode.STATIC)


    # Handle pie charts separately
    if plot_function == "pie":
        df[x_col].value_counts().plot.pie(autopct='%1.1f%%', ax=ax, **kwargs)
    else:
        plot_function(data=df, x=x_col, y=y_col, hue=hue, ax=ax, **kwargs)
        configure_axis_ticks(ax, df, x_col, y_col)

    # Add legend if hue is specified
    if hue:
        ax.legend(title=format_label(hue), bbox_to_anchor=(1, 1), loc="upper left", fontsize=10)

    # Add title and labels
    ax.set_title(title, fontsize=16, color='white')
    ax.set_xlabel(format_label(x_col), fontsize=12, color='white')
    ax.set_ylabel(format_label(y_col) if y_col else "", fontsize=12, color='white')

    plt.grid(color="gray", linestyle="--", linewidth=0.5)

    # Rotate x-axis labels if they are too long
    x_labels = [tick.get_text() for tick in plt.gca().get_xticklabels()]
    rotation = 45 if any(len(label) > 5 for label in x_labels) else 0
    plt.xticks(color='white', rotation=rotation, ha='right' if rotation else 'center')

    # Tidy the layout
    plt.tight_layout()
    return fig
