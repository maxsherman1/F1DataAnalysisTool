import logging
from dash.dependencies import Input, Output, State
from dash import html
import pandas as pd
import api.data_preprocessing as dp
from analysis.analysis_main import run_analysis

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def register_analysis_callbacks(app):
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
            df = dp.convert_to_numeric(df)

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