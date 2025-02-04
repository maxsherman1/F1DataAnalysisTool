import logging
import requests
from typing import Dict, Any, List, Optional
from pathlib import Path
from cache_manager import cache_data, load_cache, is_cached
from json_handler import get_inner_key_path, get_inner_data, set_inner_data, extend_inner_data

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

    # Resource type and filter validation
    VALID_RESOURCE_TYPES = {
        "circuits": {"optional": ["season", "round", "constructors", "drivers", "fastest", "grid", "results", "status"]},
        "constructors": {"optional": ["season", "round", "circuits", "drivers", "fastest", "grid", "results", "status"]},
        "constructorStandings": {"mandatory": ["season"], "optional": ["round", "constructors", "position"]},
        "drivers": {"optional": ["season", "round", "circuits", "constructors", "fastest", "grid", "results", "status"]},
        "driverStandings": {"mandatory": ["season"], "optional": ["round", "drivers", "position"]},
        "laps": {"mandatory": ["season", "round"], "optional": ["drivers", "constructors", "laps"]},
        "pitstops": {"mandatory": ["season", "round"], "optional": ["drivers", "laps", "pitstops"]},
        "qualifying": {"optional": ["season", "round", "circuits", "constructors", "drivers", "grid", "fastest", "status"]},
        "races": {"optional": ["season", "round", "circuits", "constructors", "drivers", "grid", "status"]},
        "results": {"optional": ["season", "round", "circuits", "constructors", "drivers", "fastest", "grid", "status"]},
        "seasons": {"optional": ["season", "circuits", "constructors", "drivers", "grid", "status"]},
        "sprint": {"optional": ["season", "round"]},
        "status": {"optional": ["status", "season", "round", "circuits", "constructors", "drivers", "results"]}
    }

    # Init function validating resource type and filters
    def __init__(self, resource_type: str, params: Optional[Dict[str, Any]] = None, filters: Optional[Dict[str, Any]] = None):
        # Input validation
        if resource_type not in self.VALID_RESOURCE_TYPES:
            raise ValueError(f"Invalid resource type: {resource_type}. Must be one of {list(self.VALID_RESOURCE_TYPES.keys())}")

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
        valid_filters = self.VALID_RESOURCE_TYPES[self.get_resource_type()]
        mandatory = valid_filters.get("mandatory", [])
        optional = valid_filters.get("optional", [])

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

        :param endpoint: API endpoint
        :param params: Query parameters for the API call (e.g., limit and offset)
        :param use_cache: Whether to use cached data if available
        :return: JSON response from the API
        """

        # Return cached file if cache is enabled and cache file exists
        if use_cache and is_cached(self.get_cache_file_name_params()):
            return load_cache(self.get_cache_file_name_params())

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
                cache_data(self.get_cache_file_path_params(), data)

            # Return the response in JSON format
            return data

        # Error handling if an error occurs during data retrieval
        except requests.exceptions.RequestException as e:
            logging.error(f"Error retrieving data from {url} with params {self.get_params()}: {e}")
            return {"error": str(e)}

    # Retrieve all data from endpoint using pagination
    def get_all_data(self, use_cache: bool = True) -> Dict[str, Any]:

        # Return cached file if cache is enabled and cache file exists
        if use_cache and is_cached(self.get_cache_file_path_all()):
            return load_cache(self.get_cache_file_path_all())

        # Retrieve initial data
        data = self.get_data(use_cache=False)

        # Retrieve total number of datapoints if there are no errors during data retrieval
        if "error" in data:
            return data

        # Retrieve total number of datapoints
        total = int(data.get("MRData", {}).get("total", 0))

        # Get the path of the inner key
        inner_key_path = get_inner_key_path(data, self.get_resource_type())

        # Error handling for inner key identification
        if not inner_key_path:
            return {"error": "Inner data path not identified in response"}

        # Extract metadata
        inner_data = []
        all_data = set_inner_data(data, inner_key_path, inner_data)

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
            inner_paginated_data = get_inner_data(paginated_data, inner_key_path)
            inner_data = extend_inner_data(inner_data, inner_paginated_data)

        all_data = set_inner_data(all_data, inner_key_path, inner_data)

        # Cache data if cache is enabled
        if use_cache:
            cache_data(self.get_cache_file_path_all(), all_data)

        # Return the paginated data
        return all_data


    # Get inner data function using the JSON handler
    def get_inner_data(self) -> List:
        data = self.get_all_data()
        inner_key_path = get_inner_key_path(data, resource_type=self.get_resource_type())
        return get_inner_data(data, inner_key_path)

    def get_cache_file_path_params(self) -> Path:
        return self.CACHE_DIR / f"{self.get_file_name()}_{self.get_params()['limit']}_{self.get_params()['offset']}.json"

    def get_cache_file_path_all(self) -> Path:
        return self.CACHE_DIR / f"{self.get_file_name()}_all.json"

    def get_cleaned_file_name(self) -> str:
        return f"{self.get_file_name()}_cleaned.csv"

    def get_file_name(self) -> str:
        return f"{self.get_endpoint().replace('/', '_')}"