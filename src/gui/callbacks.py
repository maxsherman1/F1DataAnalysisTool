import logging
import os
import time
from dash import dcc, html
from dash.dependencies import Input, Output, State, ALL
import pandas as pd
from enumeration.resource_types import ResourceType
from api.jolpica_api import JolpicaAPI
import api.data_preprocessing as dp
from visualisation.plot_generator import plot_chart
from visualisation.plot_saving import get_plots_directory, save_plot
from analysis.analysis_main import run_analysis

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def register_callbacks(app):
    # Callback to render dynamic filter input fields based on resource type
    @app.callback(
        Output('filter_inputs', 'children'),
        [Input('resource_type', 'value')]
    )
    def update_filters(resource_type):
        if not resource_type:
            return []

        try:
            # Fetch mandatory and optional filters for the selected resource_type
            mandatory_filters = ResourceType.get_mandatory(resource_type)
            optional_filters = ResourceType.get_optional(resource_type)

            filter_inputs = []

            # Render input fields for mandatory filters
            for filter_name in mandatory_filters:
                filter_inputs.append(html.Label(f" {filter_name.capitalize()} (required):"))
                filter_inputs.append(
                    dcc.Input(id={'type': 'dynamic-filter', 'index': filter_name}, type='text',
                              placeholder=f'Enter {filter_name}', value='')
                )

            # Render input fields for optional filters
            for filter_name in optional_filters:
                filter_inputs.append(html.Label(f" {filter_name.capitalize()} (optional):"))
                filter_inputs.append(
                    dcc.Input(id={'type': 'dynamic-filter', 'index': filter_name}, type='text',
                              placeholder=f'Enter {filter_name}', value='')
                )

            return filter_inputs

        except Exception as e:
            logging.error(f"Error retrieving filters for the selected resource: {e}")
            return [html.Div("Error loading filters, please try again.", style={"color": "red"})]

    # Callback to retrieve values from dynamic filter inputs and fetch data
    @app.callback(
        Output('stored_data', 'data'),
        [Input('retrieve_data', 'n_clicks')],
        [State('resource_type', 'value')] +  # Retrieve resource type
        [State({'type': 'dynamic-filter', 'index': ALL}, 'value')]  # Dynamically match all filter inputs

    )
    def retrieve_data(n_clicks, resource_type, *filter_values):
        if n_clicks == 0 or not resource_type:
            return None

        try:
            # Conversion from tuple to list of values
            filter_values = filter_values[0]

            # Fetch mandatory and optional filters for the selected resource type
            mandatory_filters = ResourceType.get_mandatory(resource_type)
            optional_filters = ResourceType.get_optional(resource_type)

            # Construct the filter dictionary dynamically
            filter_dict = {}
            all_filters = mandatory_filters + optional_filters

            # Ensure the number of filter values matches the number of filters
            if len(filter_values) != len(all_filters):
                logging.error(
                    f"Mismatch in number of filters: {len(filter_values)} values for {len(all_filters)} filters.")
                return None

            for i, filter_name in enumerate(all_filters):
                val = filter_values[i]
                if val not in [None, '']:
                    filter_dict[filter_name] = val

            # Check for missing mandatory filters
            missing_filters = [f for f in mandatory_filters if f not in filter_dict]
            if missing_filters:
                logging.error(f"Missing mandatory filters: {missing_filters}")
                return None

            # Fetch data using API
            logging.info(f"Fetching data for {resource_type} with filters: {filter_dict}")
            df = JolpicaAPI(resource_type=resource_type.replace(" ", ""), filters=filter_dict).get_cleaned_data()

            return df.to_json(date_format='iso', orient='split')

        except Exception as e:
            logging.error(f"Error fetching data: {e}")
            return None

    # Callback to enable/disable the 'Retrieve Data' button based on filter completion
    @app.callback(
        Output('retrieve_data', 'disabled'),
        [Input('resource_type', 'value')],
        [Input({'type': 'dynamic-filter', 'index': ALL}, 'value')]  # Dynamically match all filter inputs
    )
    def update_retrieve_data_button(resource_type, *filter_values):
        if not resource_type:
            return True  # Disable button if no resource type is selected

        mandatory_filters = ResourceType.get_mandatory(resource_type)

        if not mandatory_filters:
            return False  # Enable button if no mandatory filters for the resource type

        filter_values = filter_values[0]

        # Check if all mandatory filters are populated
        missing_filters = [f for f, val in zip(mandatory_filters, filter_values) if not val]

        if missing_filters:
            return True  # Disable button if not all mandatory filters are filled

        return False  # Enable button if all mandatory filters are filled

    @app.callback(
        [Output('x_axis', 'options'),
         Output('y_axis', 'options'),
         Output('group_by', 'options')],
        [Input('stored_data', 'data'),
         Input('x_axis', 'value'),
         Input('y_axis', 'value'),
         Input('group_by', 'value')]
    )
    def update_plot_column_options(stored_data, x_col, y_col, group_by):
        if not stored_data:
            return [], [{'label': 'None', 'value': 'none'}], [{'label': 'None', 'value': 'none'}]

        data = pd.read_json(stored_data, orient='split')
        columns = dp.get_columns(data)

        filtered_x_options = [{'label': col, 'value': col} for col in columns if col not in (y_col, group_by)]
        filtered_y_options = [{'label': 'None', 'value': 'none'}] + [{'label': col, 'value': col} for col in columns if col not in (x_col, group_by)]
        filtered_group_by_options = [{'label': 'None', 'value': 'none'}] + [{'label': col, 'value': col} for col in
                                                                            columns if col not in (x_col, y_col)]

        return filtered_x_options, filtered_y_options, filtered_group_by_options

    @app.callback(
        [Output('plot_area', 'children'),
         Output('plot_figure', 'data')],
        [Input('generate_plot', 'n_clicks')],
        [State('stored_data', 'data'),
         State('plot_mode', 'value'),
         State('plot_type_dropdown', 'value'),
         State('x_axis', 'value'),
         State('y_axis', 'value'),
         State('group_by', 'value'),
         State('flip_axis', 'value')]
    )
    def update_plot(n_clicks, stored_data, plot_mode, plot_type, x_col, y_col, group_by, flip_axis):
        if n_clicks == 0 or not stored_data or not x_col:
            return dcc.Graph(), {}

        y_col = None if y_col == 'none' else y_col
        group_by = None if group_by == 'none' else group_by

        data = pd.read_json(stored_data, orient='split')

        fig = plot_chart(
            data, x_col, y_col,
            title="F1 Data Analysis Plot",
            plot_type=(plot_mode, plot_type),
            hue=group_by,
            flip_axis=flip_axis
        )

        # Static Mode: Convert to PNG
        if plot_mode == 'static':
            save_plot(fig, "cache_static", plot_type=plot_mode, file_format='png')
            save_plot(fig, "cache_static", plot_type=plot_mode, file_format='jpg')
            save_plot(fig, "cache_static", plot_type=plot_mode, file_format='pdf')
            save_plot(fig, "cache_static", plot_type=plot_mode, file_format='svg')

            timestamp = int(time.time())
            return html.Img(
                src=f"/data/plots/cache_static.png?v={timestamp}",
                style={'width': '100%', 'height': 'auto'},
                key=str(timestamp)
            ), {'figure': None, 'plot_mode': plot_mode}
        else:
            return dcc.Graph(figure=fig), {'figure': fig, 'plot_mode': plot_mode}

    @app.callback(
        Output('generate_plot', 'disabled'),
        [Input('stored_data', 'data')],
        [Input('plot_type_dropdown', 'value')],
        [Input('x_axis', 'value')]
    )
    def update_generate_plot_button(data, plot_type, x_axis):
        if data and plot_type and x_axis:
            return False
        return True

    @app.callback(
        Output('file_format', 'options'),
        Input('plot_figure', 'data')
    )
    def update_file_format_dropdown(data):
        plot_mode = data.get('plot_mode')

        file_formats = []

        file_formats.append({'label': 'PNG', 'value': 'png'})
        file_formats.append({'label': 'JPG', 'value': 'jpg'})
        file_formats.append({'label': 'PDF', 'value': 'pdf'})
        file_formats.append({'label': 'SVG', 'value': 'svg'})

        if plot_mode == "interactive":
            file_formats.append({'label': 'HTML', 'value': 'html'})

        return file_formats

    @app.callback(
        Output('download_plot', 'data'),
        [Input('save_plot', 'n_clicks')],
        [State('plot_figure', 'data'),
         State('file_format', 'value')]
    )
    def save_plot_callback(n_clicks, data, file_format):
        if n_clicks == 0 or not file_format:
            return None

        plot_mode = data.get('plot_mode')

        if plot_mode == "interactive":
            plots_dir = get_plots_directory()
            os.makedirs(plots_dir, exist_ok=True)
            filename = "cache_interactive"
            save_plot(data.get('figure'), filename, plot_type=plot_mode, file_format=file_format)
            src = os.path.join(plots_dir, f'{filename}.{file_format}')
        else:
            src = os.path.join(get_plots_directory(), f'cache_static.{file_format}')
        return dcc.send_file(src)  # Return the file to download

    @app.callback(
        Output('save_plot', 'disabled'),
        [Input('generate_plot', 'n_clicks')],
        [Input('plot_area', 'children')],
        [Input('file_format', 'value')]
    )
    def update_save_plot_button(n_clicks, plot_area, file_format):
        if n_clicks > 0 and plot_area is not None and file_format is not None:
            return False
        return True

    # Callback to update available columns based on loaded data
    @app.callback(
        [Output("column_1", "options"),
         Output("column_2", "options")],
        [Input("retrieve_data", "n_clicks"),
         Input("stored_data", "data"),
         Input("column_1", "value"),
         Input("column_2", "value")]
    )
    def update_analysis_column_options(n_clicks, stored_data, column_1, column_2):
        if n_clicks == 0 or not stored_data:
            return [], [{'label': 'None', 'value': 'none'}]

        df = pd.read_json(stored_data, orient="split")
        columns = dp.get_columns(df)

        column_1_options = [{'label': col, 'value': col} for col in columns if col != column_2]
        column_2_options = ([{'label': 'None', 'value': 'none'}] +
                            [{'label': col, 'value': col} for col in columns if col != column_1])

        return column_1_options, column_2_options

    # Callback to run the selected analysis
    @app.callback(
        Output("analysis_output", "children"),
        Input("analyze_button", "n_clicks"),
        [State("stored_data", "data"),
         State("analysis_function", "value"),
         State("column_1", "value"),
         State("column_2", "value"),
         State("additional_param", "value"),
         State("convert_to_ms", "value")]
    )
    def run_analysis_callback(n_clicks, stored_data, analysis_type, column_1, column_2, additional_param, convert_to_ms):
        if n_clicks == 0 or not analysis_type:
            return ""

        df = pd.read_json(stored_data, orient="split")
        if convert_to_ms == ["convert"]:
            df = dp.convert_to_ms(df)

        try:
            # Call the run_analysis function and pass the required arguments
            result = run_analysis(df, analysis_type, column_1, column_2, additional_param)

            # Check if the result contains an error
            if "error" in result:
                return f"Error: {result['error']}"

            # Check if the result contains a statistic and p-value
            if "statistic" in result and "p_value" in result:
                return (
                    html.Div([
                        html.P(f"Test: {analysis_type}"),
                        html.P(f"Statistic: {result['statistic']}"),
                        html.P(f"P-value: {result['p_value']}"),
                    ])
                )

            # For other results, such as trend analysis, just display the result
            elif "result" in result and "method" in result:
                return (
                    html.Div([
                        html.P(f"Method: {result['method']}"),
                        html.P(f"Result: {result['result']}"),
                    ])
                )
            else:
                return "Unexpected result format."

        except Exception as e:
            return f"Error: {str(e)}"