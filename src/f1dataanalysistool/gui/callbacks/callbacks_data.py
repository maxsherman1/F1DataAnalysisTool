import logging
from dash.dependencies import Input, Output, State, ALL
from dash import dcc, html
from f1dataanalysistool.enumeration.resource_types import ResourceType
from f1dataanalysistool.api.jolpica_api import JolpicaAPI

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def register_data_callbacks(app):
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