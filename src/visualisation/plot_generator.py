import pandas as pd
from api.jolpica_api import JolpicaAPI
from visualisation.static_plot import plot_static_chart
from visualisation.interactive_plot import plot_interactive_chart
from visualisation.plot_saving import save_plot, get_plots_directory

def generate_filename(mode: str, chart_type: str, x_col: str, y_col: str, title: str) -> str:
    filename = f"{mode}_{chart_type}_{x_col.replace('.', '_')}{'_' + y_col.replace('.', '_') if y_col else ''}_{title.replace(' ', '_')}"
    return filename.lower()

def plot_chart(
        df: pd.DataFrame, x_col: str, y_col: str = None, title: str = "",
        plot_type: tuple = ("static", "line"), saving: bool = True, save_format: str = None, **kwargs
):
    # Extract mode and specific plot type
    mode, chart_type = plot_type
    default_format = "html" if mode == "interactive" else "png"
    save_format = save_format if save_format else default_format

    # Construct filename for caching
    filename = generate_filename(mode, chart_type, x_col, y_col, title)
    save_path = get_plots_directory() / f"{filename}.{save_format}"

    # Generate plot
    if mode == "static":
        fig = plot_static_chart(df, x_col=x_col, y_col=y_col, title=title,
                                plot_type=chart_type, **kwargs)
    else:
        fig = plot_interactive_chart(df, x_col=x_col, y_col=y_col, title=title,
                                     plot_type=chart_type, **kwargs)
    if saving and not save_path.exists():
        save_plot(fig, filename=filename, plot_type=mode, file_format=save_format)

    return fig