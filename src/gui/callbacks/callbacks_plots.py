import logging
import time
import os
from dash.dependencies import Input, Output, State
from dash import dcc, html
import pandas as pd
import api.data_preprocessing as dp
from visualisation.plot_generator import plot_chart
from visualisation.plot_saving import get_plots_directory, save_plot

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def register_plot_callbacks(app):
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
        filtered_y_options = [{'label': 'None', 'value': 'none'}] + [{'label': col, 'value': col} for col in columns if
                                                                     col not in (x_col, group_by)]
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
         State('flip_axis', 'value'),
         State("convert_to_ms", "value")]
    )
    def update_plot(n_clicks, stored_data, plot_mode, plot_type, x_col, y_col, group_by, flip_axis, convert_to_ms):
        if n_clicks == 0 or not stored_data or not x_col:
            return dcc.Graph(), {}

        y_col = None if y_col == 'none' else y_col
        group_by = None if group_by == 'none' else group_by

        df = pd.read_json(stored_data, orient='split')

        if convert_to_ms == ["convert"]:
            df = dp.convert_to_ms(df)
            df = dp.convert_to_numeric(df)

        fig = plot_chart(
            df, x_col, y_col,
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