import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
from visualisation.plot_generator import plot_chart
from api.jolpica_api import JolpicaAPI
from enumeration.resource_types import ResourceType
from enumeration.plot_types import PlotType
import api.data_preprocessing as dp
import io
import base64

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
        dcc.Dropdown(id='resource_type', options=[{'label': name, 'value': name} for name in resource_types], value=None),

        html.Label("Filters:"),
        html.Div(id='filter_inputs', children=[]),

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


# Callbacks to update filters based on selected resource type
@app.callback(
    Output('filter_inputs', 'children'),
    [Input('resource_type', 'value')]
)
def update_filters(resource_type):
    if not resource_type:
        return []

    mandatory_filters = ResourceType.get_mandatory(resource_type)
    optional_filters = ResourceType.get_optional(resource_type)
    filter_inputs = []

    for filter_name in mandatory_filters:
        filter_inputs.append(
            html.Div([
                html.Label(f"{filter_name.capitalize()} (required):", style={'margin-right': '10px', 'min-width': '140px'}),
                dcc.Input(id=f'filter_{filter_name}', type='text', placeholder=f'Enter {filter_name}', required=True,
                          style={'flex': '1'})
            ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '5px'})
        )

    for filter_name in optional_filters:
        filter_inputs.append(
            html.Div([
                html.Label(f"{filter_name.capitalize()} (optional):", style={'margin-right': '10px', 'min-width': '140px'}),
                dcc.Input(id=f'filter_{filter_name}', type='text', placeholder=f'Enter {filter_name}',
                          style={'flex': '1'})
            ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '5px'})
        )

    return filter_inputs


# Callbacks to update dropdowns when resource type changes
@app.callback(
    [Output('x_axis', 'options'), Output('y_axis', 'options'), Output('group_by', 'options')],
    [Input('resource_type', 'value')],
    [State(f'filter_{f}', 'value') for f in ResourceType.get_mandatory("CIRCUITS") + ResourceType.get_optional("CIRCUITS")]  # Dummy list
)
def update_column_options(resource_type, *filter_values):
    if not resource_type:
        return [], [{'label': 'None', 'value': 'none'}], [{'label': 'None', 'value': 'none'}]

    filters = {f: v for f, v in zip(ResourceType.get_mandatory(resource_type) + ResourceType.get_optional(resource_type), filter_values) if v}
    data = JolpicaAPI(resource_type=resource_type, filters=filters).get_cleaned_data()
    columns = dp.get_columns(data)
    options = [{'label': col, 'value': col} for col in columns]

    filtered_x_options = [{'label': col, 'value': col} for col in columns]
    filtered_y_options = [{'label': 'None', 'value': 'none'}] + [{'label': col, 'value': col} for col in columns]
    filtered_group_by_options = [{'label': 'None', 'value': 'none'}] + [{'label': col, 'value': col} for col in columns]

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

    if plot_mode == 'static':
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        return go.Figure(go.Image(source='data:image/png;base64,' + img_base64))

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)