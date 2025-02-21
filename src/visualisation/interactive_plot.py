from visualisation.plot_utils import format_label, validate_columns, preprocess_data, apply_axis_flip, get_plot_function
import plotly.express as px
import pandas as pd

def plot_interactive_chart(
        df: pd.DataFrame, x_col: str, y_col: str = None, title: str = "",
        plot_type: str = "line", hue: str = None, flip_axis: list = None,
        figsize: tuple = None, theme: str = "plotly_dark", **kwargs
):
    validate_columns(df, x_col, y_col)
    df = preprocess_data(df, x_col, y_col)

    # Special handling for specific plot types
    if plot_type == "heatmap":
        df = df.corr()
        fig = px.imshow(df, color_continuous_scale="viridis", **kwargs)
    elif plot_type == "hist":
        fig = px.histogram(df, x=x_col, color=hue, **kwargs)
    elif plot_type == "pie":
        fig = px.pie(df, names=x_col, title=title, **kwargs)
    else:
        plot_function = get_plot_function(plot_type, "interactive")
        fig = plot_function(df, x=x_col, y=y_col, color=hue, title=title, **kwargs)
    fig.update_layout(template=theme)

    if figsize:
        fig.update_layout(width=figsize[0], height=figsize[1])

    # Format labels
    x_label = format_label(x_col)
    y_label = format_label(y_col) if y_col else ""
    legend_title = format_label(hue) if hue else ""

    fig.update_layout(
        xaxis_title=x_label,
        yaxis_title=y_label,
        legend_title_text=legend_title,
        title_font_size=16
    )

    # Flip axes if needed
    apply_axis_flip(fig, flip_axis, plot_type="interactive")

    if y_col and df[y_col].dtype in ['int64', 'float64'] and df[y_col].max() - df[y_col].min() < 30:
        fig.update_layout(
            yaxis=dict(
                tickmode='array',
                tickvals=list(range(int(df[y_col].min()), int(df[y_col].max()) + 1))
            )
        )

    return fig