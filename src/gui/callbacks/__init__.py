from .callbacks_data import register_data_callbacks
from .callbacks_plots import register_plot_callbacks
from .callbacks_analysis import register_analysis_callbacks

def register_callbacks(app):
    register_data_callbacks(app)
    register_plot_callbacks(app)
    register_analysis_callbacks(app)