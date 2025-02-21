import matplotlib.pyplot as plt
import pandas as pd
from api.jolpica_api import JolpicaAPI
from visualisation.static_plot import plot_static_chart
from visualisation.interactive_plot import plot_interactive_chart
from visualisation.plot_saving import save_plot, get_plots_directory

def plot_chart(
        df: pd.DataFrame, x_col: str, y_col: str = None, title: str = "",
        plot_type: tuple = ("static", "line"), saving: bool = True, save_format: str = None, **kwargs
):
    # Extract mode and specific plot type
    mode, chart_type = plot_type

    default_format = "html" if mode == "interactive" else "png"
    save_format = save_format if save_format else default_format

    # Construct filename for caching
    filename = f"{mode}_{chart_type}_{x_col.replace('.', '_')}{'_' + y_col.replace('.', '_') if y_col else ''}_{title.replace(' ', '_')}"
    filename = filename.lower()
    save_path = get_plots_directory() / f"{filename}.{save_format}"

    # Generate new plot if not already saved
    if mode == "static":
        plot_static_chart(df, x_col=x_col, y_col=y_col, title=title,
                          plot_type=chart_type, **kwargs)
        if saving and not save_path.exists():
            save_plot(plt.gcf(), filename=filename, plot_type="static", file_format=save_format)
        return plt.gcf()

    elif mode == "interactive":
        fig = plot_interactive_chart(df, x_col=x_col, y_col=y_col, title=title,
                                     plot_type=chart_type, **kwargs)
        if saving and not save_path.exists():
            save_plot(fig, filename=filename, plot_type="interactive", file_format=save_format)
        return fig