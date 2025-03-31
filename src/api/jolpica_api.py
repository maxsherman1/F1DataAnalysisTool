import logging
import requests
import api.cache_manager as cache_manager
import api.json_handler as json_handler
import api.data_preprocessing as dp
import pandas as pd
from typing import Dict, Any, List, Optional
from pathlib import Path
from enumeration.resource_types import ResourceType

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class JolpicaAPI:

    # Constants
    BASE_URL = "https://api.jolpi.ca/ergast/f1/"
    CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "data/cache"
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Parameter constants
    DEFAULT_LIMIT = 30
    MAXIMUM_LIMIT = 100
    DEFAULT_OFFSET = 0

    # Init function validating resource type and filters
    def __init__(self, resource_type: str, params: Optional[Dict[str, Any]] = None, filters: Optional[Dict[str, Any]] = None):
        # Set instance variables
        self.params = {}
        if params is not None:
            self.set_params(params)
        else:
            self.set_params({"limit": self.DEFAULT_LIMIT, "offset": self.DEFAULT_OFFSET})

        self.resource_type = None
        self.set_resource_type(resource_type)

        self.filters = {}
        if filters is not None:
            self.set_filters(filters)

        self.endpoint = None
        self.set_endpoint()

    def set_params(self, params: Dict[str, Any]) -> None:
        self.params = params

    def get_params(self) -> Dict[str, Any]:
        return self.params

    def set_resource_type(self, resource_type: str) -> None:
        self.resource_type = resource_type

    def get_resource_type(self) -> str:
        return self.resource_type

    # Set all the filters provided
    def set_filters(self, filters: Dict[str, Any]) -> None:
        # Get mandatory and optional filters for the resource type
        mandatory = ResourceType.get_mandatory(resource_type=self.resource_type)
        optional = ResourceType.get_optional(resource_type=self.resource_type)

        # Check mandatory filters to see if they are present
        for key in mandatory:
            if key not in filters:
                raise ValueError(f"Mandatory filter '{key}' not provided in {filters}")

        # Check other filters to see if they are allowed for this resource typee
        for key in filters.keys():
            if key not in mandatory + optional:
                raise ValueError(f"Invalid filter {key}")

        # Set the filters
        self.filters = filters

    # Get all filters
    def get_filters(self) -> Dict[str, Any]:
        return self.filters

    # Set the endpoint of the API request
    def set_endpoint(self) -> None:
        endpoint_parts = []
        filters = self.get_filters().copy()

        # Add season and round first if present
        season = filters.pop("season", None)
        round_number = filters.pop("round", None)
        if season:
            endpoint_parts.append(season)
            if round_number:
                endpoint_parts.append(round_number)

        # Add other filters dynamically excluding position
        position = filters.pop("position", None)
        for key, value in filters.items():
            if value:
                endpoint_parts.extend([key, value])

        # Append resource type at the end if not already added
        if self.get_resource_type() not in endpoint_parts:
            endpoint_parts.append(self.get_resource_type())

        if position:
            endpoint_parts.append(position)

        self.endpoint = "/".join(endpoint_parts)

    # Get endpoint
    def get_endpoint(self) -> str:
        return self.endpoint


    def get_data(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Retrieves data from the Jolpica-F1 API with optional caching.

        :param use_cache: Whether to use cached data if available
        :return: JSON response from the API
        """

        # Return cached file if cache is enabled and cache file exists
        if use_cache and cache_manager.is_cached(self.get_cache_file_path_params()):
            return cache_manager.load_cache(self.get_cache_file_path_params())

        # Add endpoint to the base url
        url = f"{self.BASE_URL}{self.get_endpoint()}"

        # Make API call
        try:

            # Get API data and check for errors
            response = requests.get(url, params=self.get_params())
            response.raise_for_status()
            data = response.json()

            # Save data to cache file if cache is enabled
            if use_cache:
                cache_manager.cache_data(self.get_cache_file_path_params(), data)

            # Return the response in JSON format
            return data

        # Error handling if an error occurs during data retrieval
        except requests.exceptions.RequestException as e:
            logging.error(f"Error retrieving data from {url} with params {self.get_params()}: {e}")
            return {"error": str(e)}

    # Retrieve all data from endpoint using pagination
    def get_all_data(self, use_cache: bool = True) -> Dict[str, Any]:

        # Return cached file if cache is enabled and cache file exists
        if use_cache and cache_manager.is_cached(self.get_cache_file_path_all()):
            return cache_manager.load_cache(self.get_cache_file_path_all())

        # Retrieve initial data
        data = self.get_data(use_cache=False)

        # Retrieve total number of datapoints if there are no errors during data retrieval
        if "error" in data:
            return data

        # Retrieve total number of datapoints
        total = int(data.get("MRData", {}).get("total", 0))

        # Get the path of the inner key
        inner_key_path = json_handler.get_inner_key_path(data, self.get_resource_type())

        # Error handling for inner key identification
        if not inner_key_path:
            return {"error": "Inner data path not identified in response"}

        # Extract metadata
        inner_data = []
        all_data = json_handler.set_inner_data(data, inner_key_path, inner_data)

        # Set parameters
        self.set_params({"limit": self.MAXIMUM_LIMIT, "offset": self.DEFAULT_OFFSET})

        # Pagination handler loop
        for offset in range(0, total, self.get_params()["limit"]):

            # Set offset and retrieve data
            self.set_params({"limit": self.MAXIMUM_LIMIT, "offset": offset})
            paginated_data = self.get_data(use_cache=False)

            # Error handling
            if "error" in paginated_data:
                logging.warning(f"Error during pagination at offset {offset}")
                break

            # Append data to the inner key list
            inner_paginated_data = json_handler.get_inner_data(paginated_data, inner_key_path)
            inner_data = json_handler.extend_inner_data(inner_data, inner_paginated_data)

        all_data = json_handler.set_inner_data(all_data, inner_key_path, inner_data)

        # Cache data if cache is enabled
        if use_cache:
            cache_manager.cache_data(self.get_cache_file_path_all(), all_data)

        # Return the paginated data
        return all_data


    # Get inner data function using the JSON handler
    def get_inner_data(self) -> List:
        data = self.get_all_data()
        inner_key_path = json_handler.get_inner_key_path(data, resource_type=self.get_resource_type())
        return json_handler.get_inner_data(data, inner_key_path)

    def get_cache_file_path_params(self) -> Path:
        return self.CACHE_DIR / f"{self.get_file_name()}_{self.get_params()['limit']}_{self.get_params()['offset']}.json"

    def get_cache_file_path_all(self) -> Path:
        return self.CACHE_DIR / f"{self.get_file_name()}_all.json"

    def get_cleaned_file_name(self) -> str:
        return f"{self.get_file_name()}_cleaned.csv"

    def get_file_name(self) -> str:
        return f"{self.get_endpoint().replace('/', '_')}"

    def get_cleaned_data(self) -> pd.DataFrame:
        file_name = self.get_cleaned_file_name()

        if dp.is_loaded_csv(file_name):
            return dp.load_from_csv(file_name)

        flattened_data = dp.preprocess_data(self.get_inner_data())
        df = dp.convert_to_dataframe(flattened_data)
        df = dp.validate_data(df)
        df = dp.convert_to_numeric(df)
        dp.save_to_csv(df, file_name)
        return df