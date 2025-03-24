from dash import dcc, html

from enumeration.plot_types import PlotType
from enumeration.resource_types import ResourceType

def create_layout(app):
    return html.Div([
        html.H1("F1 Data Analysis Tool", style={"textAlign": "center"}),

        # Data Retrieval Section (Shared across all tabs)
        html.Div([
            html.H3("Retrieve F1 Data"),
            html.Label("Select Resource Type:"),
            dcc.Dropdown(id='resource_type', options=[{'label': name, 'value': name.lower()} for name in ResourceType.get_all_names()],
                         placeholder="Select Resource Type"),

            html.Label("Filters:"),
            html.Div(id='filter_inputs', children=[]),

            dcc.Store(id='filters_metadata', storage_type='memory'),

            html.Button('Retrieve Data', id='retrieve_data', n_clicks=0, className="btn-primary"),
            dcc.Store(id='stored_data'),
        ], className="data-section"),

        dcc.Tabs(id="tabs", value="visualisation", children=[
            dcc.Tab(label="Visualisation", value="visualisation", children=[
                html.Div([
                    html.Div([
                        html.H3("Visualisation Settings"),
                        html.Label("Select Plot Type:"),
                        dcc.Dropdown(id='plot_type_dropdown', options=[{'label': name.capitalize(), 'value': name} for name in PlotType.get_all_names()],
                                     placeholder="Select Plot Type"),

                        html.Label("Select X-axis:"),
                        dcc.Dropdown(id='x_axis', placeholder="Select X-axis", clearable=False),

                        html.Label("Select Y-axis:"),
                        dcc.Dropdown(id='y_axis', placeholder="Select Y-axis"),

                        html.Label("Group by:"),
                        dcc.Dropdown(id='group_by', placeholder="Select Group By"),

                        html.Label("Plot Mode:"),
                        dcc.RadioItems(id='plot_mode', options=[
                            {'label': 'Static', 'value': 'static'},
                            {'label': 'Interactive', 'value': 'interactive'}
                        ], value='interactive', inline=True),

                        dcc.Checklist(
                            id='flip_axis',
                            options=[
                                {'label': 'Flip X axes', 'value': 'flip_x'},
                                {'label': 'Flip Y axes', 'value': 'flip_y'}
                            ],
                            value=[]
                        ),

                        html.Button('Generate Plot', id='generate_plot', n_clicks=0),
                        html.Button('Save Plot', id='save_plot', n_clicks=0),
                    ], style={'flex': 1, 'padding': '10px'}),

                    # Visualisation Output
                    html.Div([
                        dcc.Graph(id='plot_area')
                    ], style={'flex': 3, 'padding': '10px'}),
                ], style={'display': 'flex', 'width': '100%', 'height': '80%'}),
            ]),
            dcc.Tab(label="Data Analysis", value="analysis", children=[
                html.Div([
                    html.Div([
                        html.H3("Statistical Analysis"),
                        html.Label("Select Analysis Function:"),
                        dcc.Dropdown(id="analysis_function", placeholder="Choose an analysis function..."),

                        html.Label("Select Column 1:"),
                        dcc.Dropdown(id="column_1", placeholder="Select first column", clearable=True),

                        html.Label("Select Column 2 (if required):"),
                        dcc.Dropdown(id="column_2", placeholder="Select second column", clearable=True),

                        html.Label("Additional Parameter (if required):"),
                        dcc.Input(id="additional_param", type="text", placeholder="Enter additional parameter"),

                        html.Button("Analyze Data", id="analyze_button", n_clicks=0),
                    ], style={'flex': 1, 'padding': '10px'}),

                    # Analysis Output
                    html.Div(id="analysis_output", style={'flex': 3, 'padding': '10px'})

                ], style={'display': 'flex', 'width': '100%', 'height': '80%'})
            ]),
        ]),
    ])
