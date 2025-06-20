from f1dataanalysistool.visualisation.plot_utils import format_label, apply_axis_flip, configure_axis_ticks
from f1dataanalysistool.enumeration.plot_types import PlotMode, PlotType, PlotFunction
import pandas as pd

def plot_interactive_chart(
        df: pd.DataFrame, x_col: str, y_col: str = None, title: str = "",
        plot_type: str = "line", hue: str = None, flip_axis: list = None,
        figsize: tuple = (1500, 600), theme: str = None, **kwargs
):
    plot_function = PlotFunction.get_plot_function(plot_type=PlotType(plot_type), mode=PlotMode.INTERACTIVE)

    # Special handling for specific plot types
    if plot_type == "heatmap":
        fig = plot_function(df.corr(), color_continuous_scale="viridis", **kwargs)
    elif plot_type == "pie":
        fig = plot_function(df, names=x_col, title=title, **kwargs)
    else:
        fig = plot_function(df, x=x_col, y=y_col, color=hue, title=title, **kwargs)
        configure_axis_ticks(fig, df, x_col, y_col)

    fig.update_layout(template=theme, width=figsize[0], height=figsize[1])

    fig.update_layout(
        xaxis_title=format_label(x_col),
        yaxis_title=format_label(y_col) if y_col else "",
        legend_title_text=format_label(hue) if hue else "",
        title_font_size=16
    )

    # Flip axes if needed
    apply_axis_flip(fig, flip_axis, plot_type="interactive")


    return fig