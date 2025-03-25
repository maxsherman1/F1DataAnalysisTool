from dash import Dash
from layout import create_layout
from callbacks import register_callbacks
from flask import send_from_directory
from visualisation.plot_saving import get_plots_directory

# Initialize Dash app
app = Dash(__name__, suppress_callback_exceptions=True)
app.layout = create_layout(app)

# Register callbacks
register_callbacks(app)

@app.server.route('/data/plots/<path:filename>')
def serve_plot(filename):
    return send_from_directory(get_plots_directory(), filename)

if __name__ == "__main__":
    app.run_server(debug=True)
