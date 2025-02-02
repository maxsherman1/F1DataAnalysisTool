import logging
import requests
from typing import Dict, Any, Optional
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
    DEFAULT_LIMIT = 30
    MAXIMUM_LIMIT = 100
    DEFAULT_OFFSET = 0
    VALID_RESOURCE_TYPE = {
        "circuits", "constructors", "constructorStandings", "drivers",
        "driverStandings", "laps", "pitstops", "qualifying", "races",
        "results", "seasons", "status"
    }

    def __init__(self, resource_type: str, **filters):
        if resource_type not in self.VALID_RESOURCE_TYPE:
            raise ValueError(f"Invalid resource type: {resource_type}. Must be one of {list(self.VALID_RESOURCE_TYPE)}")

        self.resource_type = resource_type
        self.filters = {}
        self.set_filters(filters)

    def set_filters(self, filters: Dict[str, Any]):
        self.filters = filters

    def get_filters(self) -> Dict[str, Any]:
        return self.filters

    def set_filter(self, key: str, value: Any):
        self.filters[key] = value

    def get_data(self, endpoint: str, params: Optional[Dict[str, Any]] = None, use_cache: bool = True) -> Dict[str, Any]:
        """
        Retrieves data from the Jolpica-F1 API with optional caching.

        :param endpoint: API endpoint
        :param params: Query parameters for the API call (e.g., limit and offset)
        :param use_cache: Whether to use cached data if available
        :return: JSON response from the API
        """
        # Set default parameters if no parameters are provided
        params = params or {"limit": self.DEFAULT_LIMIT, "offset": self.DEFAULT_OFFSET}

        # Cache file name
        cache_file = self.CACHE_DIR / f"{endpoint.replace('/', '_')}_{params['limit']}_{params['offset']}.json"

        # Return cached file if cache is enabled and cache file exists
        if use_cache and is_cached(cache_file):
            return load_cache(cache_file)

        # Add endpoint to the base url
        url = f"{self.BASE_URL}{endpoint}"

        # Make API call
        try:

            # Get API data and check for errors
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Save data to cache file if cache is enabled
            if use_cache:
                cache_data(cache_file, data)

            # Return the response in JSON format
            return data

        # Error handling if an error occurs during data retrieval
        except requests.exceptions.RequestException as e:
            logging.error(f"Error retrieving data from {url} with params {params}: {e}")
            return {"error": str(e)}

    # Retrieve all data from endpoint using pagination
    def get_all_data(self, use_cache: bool = True) -> Dict[str, Any]:

        # Get data retrieval endpoint
        endpoint = self.build_endpoint()

        # return cache file if file is found in cache folder
        cache_file = self.CACHE_DIR / f"{endpoint.replace('/', '_')}_all.json"

        # Return cached file if cache is enabled and cache file exists
        if use_cache and is_cached(cache_file):
            return load_cache(cache_file)

        # Retrieve initial data
        data = self.get_data(endpoint, use_cache=False)

        # Retrieve total number of datapoints if there are no errors during data retrieval
        if "error" in data:
            return data

        # Retrieve total number of datapoints
        total = int(data.get("MRData", {}).get("total", 0))

        # Get the path of the inner key
        inner_key_path = get_inner_key_path(data, self.resource_type)

        # Error handling for inner key identification
        if not inner_key_path:
            return {"error": "Inner data path not identified in response"}

        # Extract metadata
        inner_data = []
        all_data = set_inner_data(data, inner_key_path, inner_data)

        # Set parameters
        params = {"limit": self.MAXIMUM_LIMIT, "offset": self.DEFAULT_OFFSET}

        # Pagination handler loop
        for offset in range(0, total, params["limit"]):

            # Set offset and retrieve data
            params["offset"] = offset
            paginated_data = self.get_data(endpoint, params, use_cache=False)

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
            cache_data(cache_file, all_data)

        # Return the paginated data
        return all_data

    # Builds the endpoint URL dynamically based on filters
    def build_endpoint(self) -> str:
        endpoint_parts = []

        # Add season and round first if present
        season = self.filters.pop("season", None)
        round_number = self.filters.pop("round", None)
        if season:
            endpoint_parts.append(season)
            if round_number:
                endpoint_parts.append(round_number)

        # Add other filters dynamically excluding position
        position = self.filters.pop("position", None)
        for key, value in self.filters.items():
            if value:
                endpoint_parts.extend([key, value])

        # Append resource type at the end if not already added
        if self.resource_type not in endpoint_parts:
            endpoint_parts.append(self.resource_type)

        if position:
            endpoint_parts.append(position)

        return "/".join(endpoint_parts)