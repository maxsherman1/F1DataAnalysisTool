from dash import Dash
from layout import create_layout
from callbacks import register_callbacks

# Initialize Dash app
app = Dash(__name__, suppress_callback_exceptions=True)
app.layout = create_layout(app)

# Register callbacks
register_callbacks(app)

if __name__ == "__main__":
    app.run_server(debug=True)
