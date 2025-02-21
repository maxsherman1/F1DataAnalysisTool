import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
from visualisation.plot_generator import plot_chart
from api.jolpica_api import JolpicaAPI
from enumeration.resource_types import ResourceType
from enumeration.plot_types import PlotType
import api.data_preprocessing as dp

# Get plot types
plot_types = [pt.value.capitalize() for pt in PlotType]

# Get resource types
resource_types = ResourceType.get_all_names()

# Initialize Dash app
app = dash.Dash(__name__)

# Define layout
app.layout = html.Div([
    html.H1("F1 Data Analysis Tool"),

    # Controls
    html.Div([
        html.Label("Select Resource Type:"),
        dcc.Dropdown(id='resource_type', options=[{'label': name, 'value': name} for name in resource_types],
                     value=None),

        html.Label("Select Plot Type:"),
        dcc.Dropdown(id='plot_type_dropdown', options=[{'label': pt, 'value': pt.lower()} for pt in plot_types],
                     value='line'),

        html.Label("Select X-axis:"),
        dcc.Dropdown(id='x_axis', options=[], value=None, placeholder="Select X-axis", clearable=False),

        html.Label("Select Y-axis:"),
        dcc.Dropdown(id='y_axis', options=[{'label': 'None', 'value': 'none'}], value='none',
                     placeholder="Select Y-axis"),

        html.Label("Group by:"),
        dcc.Dropdown(id='group_by', options=[{'label': 'None', 'value': 'none'}], value='none',
                     placeholder="Select Group By"),

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


# Callbacks to update dropdowns when resource type changes
@app.callback(
    [Output('x_axis', 'options'), Output('y_axis', 'options'), Output('group_by', 'options')],
    [Input('resource_type', 'value'), Input('x_axis', 'value'), Input('y_axis', 'value'), Input('group_by', 'value')]
)
def update_column_options(resource_type, x_col, y_col, group_by):
    if not resource_type:
        return [], [{'label': 'None', 'value': 'none'}], [{'label': 'None', 'value': 'none'}]

    data = JolpicaAPI(resource_type=resource_type).get_cleaned_data()
    columns = dp.get_columns(data)
    options = [{'label': col, 'value': col} for col in columns]

    filtered_x_options = [{'label': col, 'value': col} for col in columns if col not in (y_col, group_by)]
    filtered_y_options = [{'label': 'None', 'value': 'none'}] + [{'label': col, 'value': col} for col in columns if col not in (x_col, group_by)]
    filtered_group_by_options = [{'label': 'None', 'value': 'none'}] + [{'label': col, 'value': col} for col in columns if col not in (x_col, y_col)]

    return filtered_x_options, filtered_y_options, filtered_group_by_options


# Callbacks
@app.callback(
    Output('plot_area', 'figure'),
    [Input('generate_plot', 'n_clicks')],
    [State('resource_type', 'value'), State('x_axis', 'value'),
     State('y_axis', 'value'), State('group_by', 'value'), State('plot_mode', 'value'),
     State('plot_type_dropdown', 'value'), State('flip_axis', 'value')]
)
def update_plot(n_clicks, resource_type, x_col, y_col, group_by, plot_mode, plot_type, flip_axis):
    if not x_col or not resource_type:
        return go.Figure()

    y_col = None if y_col == 'none' else y_col
    group_by = None if group_by == 'none' else group_by

    data = JolpicaAPI(resource_type=resource_type).get_cleaned_data()
    fig = plot_chart(data, x_col, y_col, title=f"F1 {resource_type} Analysis", plot_type=(plot_mode, plot_type),
                     flip_axis=['x'] if 'flip_x' in flip_axis else (['y'] if 'flip_y' in flip_axis else None))
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)