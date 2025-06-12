from dash import Dash
from flask import send_from_directory
from f1dataanalysistool.gui.layout import create_layout
from f1dataanalysistool.gui.callbacks import register_callbacks
from f1dataanalysistool.visualisation.plot_saving import get_plots_directory

# Initialize Dash app
app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # Expose the server variable for Render
app.layout = create_layout(app)

# Register callbacks
register_callbacks(app)

@app.server.route('/data/plots/<path:filename>')
def serve_plot(filename):
    return send_from_directory(get_plots_directory(), filename)

if __name__ == "__main__":
    app.run_server(debug=False, host='0.0.0.0', port=8080)
