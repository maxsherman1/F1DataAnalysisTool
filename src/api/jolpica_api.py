import json
import logging
import os
import requests
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# The base URL for the API
BASE_URL = "https://api.jolpi.ca/ergast/f1/"

CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "data/cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def get_data(endpoint, params=None, use_cache=True):
    """
    Retrieves data from the Jolpica-F1 API with optional caching.

    :param endpoint: API endpoint
    :param params: Query parameters for the API call (e.g., limit and offset)
    :param use_cache: Whether to use cached data if available
    :return: JSON response from the API
    """
    # Extract parameters
    limit = params.get("limit")
    offset = params.get("offset")

    # Cache file name
    file_name = f"{endpoint.replace('/', '_')}_{limit}_{offset}.json"

    # return cache file if file is found in cache folder
    if file_name in os.listdir(CACHE_DIR):
        return load_cache(file_name)

    # Add enpoint to the base url
    url = f"{BASE_URL}{endpoint}"

    # Make API call
    try:

        # Get API data and check for errors
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Save data to cache file if cache is enabled
        if use_cache:
            cache_data(file_name, data)

        # Return the response in JSON format
        return data

    # Error handling if an error occurs during data retrieval
    except requests.exceptions.RequestException as e:
        logging.error(f"Error retrieving data: \n{e}")
        return "Exception request"

# Retrieve all data from endpoint using pagination
def get_all_data(endpoint, use_cache=True):

    # Initiate variables
    limit = 0
    offset = 0
    params = {"limit": limit, "offset": offset}
    all_data = {}

    # Retrieve initial data
    data = get_data(endpoint, params, False)

    # Retrieve total number of datapoints if there are no errors during data retrieval
    if data == "Exception request":
        return data
    else:
        total = int(data.get("MRData").get("total"))

    # If number of datapoints is less than the maximum limit of 100, no pagination is necessary
    if total <= 100:
        limit = total
        offset = 0
        params = {"limit": limit, "offset": offset}
        all_data = get_data(endpoint, params, False)

    # If there is more datapoints than the limit, a loop will paginate through the API endpoint
    elif total > 100:
        limit = 100
        offset = 0
        all_data = data
        dynamic_key = None

        for key in data.get("MRData").keys():
            if key not in ["xmlns", "series", "url", "limit", "offset", "total"]:
                dynamic_key = key
                break

        if not dynamic_key:
            logging.error("Unable to identify dynamic key")
            return "Error: unable to process data structure"

        inner_key = None
        dynamic_value = data["MRData"].get(dynamic_key)
        if isinstance(dynamic_value, dict):
            for key in dynamic_value.keys():
                inner_key = key
                break

        if not inner_key:
            logging.error("Unable to find inner key in dynamic key")
            return "Error: unable to find inner key"

        all_data["MRData"][dynamic_key][inner_key] = []

        while offset < total:
            params = {"limit": limit, "offset": offset}
            paginated_data = get_data(endpoint, params, False)
            logging.info(f"Received data with limit {limit} and offset {offset}")

            if paginated_data == "Exception request":
                logging.error("An error occurred while fetching paginated data.")
                break

            paginated_dynamic_data = (
                paginated_data.get("MRData").
                get(dynamic_key).
                get(inner_key)
            )

            all_data["MRData"][dynamic_key][inner_key].extend(paginated_dynamic_data)
            logging.info(f"Appended {len(paginated_dynamic_data)} items from offset {offset}")
            offset += limit

    # Cache data if cache is enabled
    if use_cache:
        cache_file = f"{endpoint.replace('/', '_')}_all.json"
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

def main():
    print(get_all_data("constructors"))
    print(get_all_data("drivers"))

if __name__ == "__main__":
    main()