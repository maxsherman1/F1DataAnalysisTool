import json
import logging
import os
import requests
from pathlib import Path

#  Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Constants
BASE_URL = "https://api.jolpi.ca/ergast/f1/"
CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "data/cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_LIMIT = 30
MAXIMUM_LIMIT = 100
DEFAULT_OFFSET = 0

def get_data(endpoint, params=None, use_cache=True):
    """
    Retrieves data from the Jolpica-F1 API with optional caching.

    :param endpoint: API endpoint
    :param params: Query parameters for the API call (e.g., limit and offset)
    :param use_cache: Whether to use cached data if available
    :return: JSON response from the API
    """
    # Set default parameters if no parameters are provided
    if params is None:
        params = {"limit": DEFAULT_LIMIT, "offset": DEFAULT_OFFSET}

    # Extract parameters
    limit = params.get("limit")
    offset = params.get("offset")

    # Cache file name
    cache_file = f"{endpoint.replace('/', '_')}_{limit}_{offset}.json"

    # Return cached file if cache is enabled and cache file exists
    if use_cache and is_cached(cache_file):
        return load_cache(cache_file)

    # Add endpoint to the base url
    url = f"{BASE_URL}{endpoint}"

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
def get_all_data(resource_type, endpoint, use_cache=True):

    # return cache file if file is found in cache folder
    cache_file = f"{endpoint.replace('/', '_')}_all.json"

    # Return cached file if cache is enabled and cache file exists
    if use_cache and is_cached(cache_file):
        return load_cache(cache_file)

    # Retrieve initial data
    data = get_data(endpoint, use_cache=False)

    # Retrieve total number of datapoints if there are no errors during data retrieval
    if "error" in data:
        return data

    # Set parameters
    limit = MAXIMUM_LIMIT
    offset = DEFAULT_OFFSET
    params = {"limit": limit, "offset": offset}

    # Get total and dynamic keys for pagination handling
    total = int(data.get("MRData").get("total"))
    dynamic_key, inner_key_path = get_dynamic_keys(data, resource_type)

    if not dynamic_key or not inner_key_path:
        return {"error": "Dynamic keys not identified in response"}

    # Extract metadata
    all_data = remove_inner_data(data, dynamic_key, inner_key_path)

    # Pagination handler loop
    for offset in range(0, total, params["limit"]):

        # Set offset and retrieve data
        params["offset"] = offset
        paginated_data = get_data(endpoint, params, use_cache=False)

        # Error handling
        if "error" in paginated_data:
            logging.warning(f"Error during pagination at offset {offset}")
            break

        # Append data to the inner key list
        inner_paginated_data = find_inner_data(paginated_data, dynamic_key, inner_key_path)
        all_data = extend_inner_data(all_data, dynamic_key, inner_key_path, inner_paginated_data)
        print(f"Length of inner paginated data: {len(inner_paginated_data)}")

    # Cache data if cache is enabled
    if use_cache:
        cache_data(cache_file, all_data)

    # Return the paginated data
    return all_data

# Cache data function (does not check if cache folder is present)
def cache_data(file_name, data):
    cache_file = f"{CACHE_DIR}/{file_name}"
    with open(cache_file, "w") as f:
        json.dump(data, f)
    logging.info(f"Data cached to {file_name} successfully.")

# Load data function (does not check if cache file is present)
def load_cache(file_name):
    cache_file = f"{CACHE_DIR}/{file_name}"
    with open(cache_file, "r") as f:
        logging.info(f"Data loaded from {file_name} successfully.")
        return json.load(f)

# Checks if cache file is in the cache directory
def is_cached(file_name):
    return (CACHE_DIR / file_name).exists()

# Retrieves resource data dynamically based on filters
def get_resource(resource_type, **filters):
    endpoint = build_endpoint(resource_type, **filters)
    return get_all_data(resource_type, endpoint)

# Builds the endpoint URL dynamically based on filters
def build_endpoint(resource_type, **filters):
    endpoint_parts = []

    # Add season and round first
    if filters.get("season"):
        endpoint_parts.append(filters["season"])
        if filters.get("round"):
            endpoint_parts.append(filters["round"])

    # Add other filters dynamically
    for key, value in filters.items():
        if key not in ["season", "round", "position"] and value:
            endpoint_parts.extend([key.replace("_id", ""), value])

    # Append resource type at the end if not already added
    if resource_type not in endpoint_parts:
        endpoint_parts.append(resource_type)

    if filters.get("position"):
        endpoint_parts.append(filters["position"])

    return "/".join(endpoint_parts)

def get_inner_key_path(data, resource_type):
    def search_inner_keys(nested_dict, target, path=None):
        if path is None:
            path = []

        # Resource type input filtering
        resources = ["results", "qualifying"]
        if target.lower() in resources:
            target = "Races"

        # if the provided dictionary is not a dictionary nor list, return None
        if not isinstance(nested_dict, (dict, list)):
            print(f"Target {target} not found in current path: {path}")
            return None

        # If the argument is a list, retrieve the first value (will always be a dictionary)
        if isinstance(nested_dict, list):
            nested_dict = nested_dict[0] if nested_dict else None

        # get the key of the last entry of the dictionary
        last_key = list(nested_dict)[-1] if nested_dict else None

        # Check if the target has been found
        if last_key and last_key.lower() == target.lower():
            return path + [last_key]

        # retrieve the value paired with the key
        value = nested_dict.get(last_key) if nested_dict else None

        if isinstance(value, (dict, list)):
            return search_inner_keys(value, target, path + [last_key])

        return None
    return search_inner_keys(data.get("MRData", {}), resource_type)

# Remove the inner data and return the common data structure
def remove_inner_data(data, inner_key_path):
    # Retrieve second to last inner data
    inner_data = find_inner_data(data, inner_key_path, return_parent=True)

    # Get last key
    last_key = inner_key_path[-1]
    if isinstance(inner_data, list):
        inner_data = inner_data[0] # Handles lists if present
    # If last key is in inner data, replace it with an empty list
    if last_key in inner_data.keys():
        inner_data[last_key] = []

    # Return the data
    return data

# find the inner data and returns it
def find_inner_data(data, inner_key_path, return_parent=False):
    # Retrieve initial inner data
    inner_data = data["MRData"]
    x = -1 if return_parent else len(inner_key_path)

    # Loop through the path list until the final value has been found
    for key in inner_key_path[:x]:
        if isinstance(inner_data, list):
            inner_data = inner_data[0]
        inner_data = inner_data[key]

    # Return inner data
    return inner_data

# Extend the inner data with additional provided data
def extend_inner_data(data, dynamic_key, inner_key_path, additional_data):

    # Get second to last inner data
    inner_data = find_inner_data(data, dynamic_key, inner_key_path, True)

    # Get last key
    last_key = inner_key_path[-1]

    # If the key is in the inner data
    if last_key in inner_data.keys():
        # Chcek if not a list
        if not isinstance(inner_data[last_key], list):
            raise TypeError(f"Expected a list at {last_key}, but found {type(inner_data[last_key])}.")
        # Extend additional data
        inner_data[last_key].extend(additional_data)
        logging.info(f"inner_data_extended successfully at {last_key}")

    # return data
    return data