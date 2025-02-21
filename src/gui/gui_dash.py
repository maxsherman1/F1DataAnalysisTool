import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
from visualisation.plot_generator import plot_chart
from api.jolpica_api import JolpicaAPI

# Initialize Dash app
app = dash.Dash(__name__)

# Define layout
app.layout = html.Div([
    html.H1("F1 Data Analysis Tool"),

    # Controls
    html.Div([
        html.Label("Select Resource Type:"),
        dcc.Dropdown(id='resource_type', options=[], value=None),

        html.Label("Select Plot Type:"),
        dcc.Dropdown(id='plot_type_dropdown', options=[], value='line'),

        html.Label("Select X-axis:"),
        dcc.Dropdown(id='x_axis', options=[], value=None),

        html.Label("Select Y-axis:"),
        dcc.Dropdown(id='y_axis', options=[], value=None),

        html.Label("Group by:"),
        dcc.Dropdown(id='group_by', options=[], value=None),

        dcc.RadioItems(
            id='plot_mode',
            options=[
                {'label': 'Static', 'value': 'static'},
                {'label': 'Interactive', 'value': 'interactive'}
            ],
            value='interactive'
        ),

        dcc.Checklist(
            id='flip_axis',
            options=[
                {'label': 'Flip X axes', 'value': 'flip_x'},
                {'label': 'Flip Y axes', 'value': 'flip_y'}
            ],
            value=[]
        ),

        html.Button('Generate Plot', id='generate_plot', n_clicks=0),
        html.Button('Save Plot', id='save_plot', n_clicks=0)
    ], style={'width': '20%', 'display': 'inline-block', 'vertical-align': 'top'}),

    # Plot display
    html.Div([dcc.Graph(id='plot_area')], style={'width': '75%', 'display': 'inline-block', 'margin-left': '5%'})
])


# Callbacks
@app.callback(
    Output('plot_area', 'figure'),
    [Input('generate_plot', 'n_clicks')],
    [State('season', 'value'), State('resource_type', 'value'), State('x_axis', 'value'),
     State('y_axis', 'value'), State('group_by', 'value'), State('plot_mode', 'value'),
     State('plot_type_dropdown', 'value'), State('flip_axis', 'value')]
)
def update_plot(n_clicks, season, resource_type, x_col, y_col, group_by, plot_mode, plot_type, flip_axis):
    if not x_col or not y_col or not resource_type:
        return go.Figure()

    data = JolpicaAPI(resource_type=resource_type, filters={"season": season}).get_cleaned_data()
    fig = plot_chart(data, x_col, y_col, title=f"F1 {season} Analysis", plot_type=(plot_mode, plot_type),
                     flip_axis=['x'] if 'flip' in flip_axis else None)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)