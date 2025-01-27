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

def get_data(endpoint, params={"limit": 30, "offset": 0}, use_cache=True):
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
    cache_file = f"{endpoint.replace('/', '_')}_{limit}_{offset}.json"

    # return cache file if file is found in cache folder
    if cache_file in os.listdir(CACHE_DIR):
        return load_cache(cache_file)

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
            cache_data(cache_file, data)

        # Return the response in JSON format
        return data

    # Error handling if an error occurs during data retrieval
    except requests.exceptions.RequestException as e:
        logging.error(f"Error retrieving data: \n{e}")
        return "Exception request"

# Retrieve all data from endpoint using pagination
def get_all_data(endpoint, use_cache=True):

    # return cache file if file is found in cache folder
    cache_file = f"{endpoint.replace('/', '_')}_all.json"
    if cache_file in os.listdir(CACHE_DIR):
        return load_cache(cache_file)

    # Initiate variables
    all_data = {}

    # Retrieve initial data
    data = get_data(endpoint, use_cache=False)

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

        dynamic_key, inner_key = get_dynamic_keys(data)

        if not dynamic_key or not inner_key:
            return {"error": "Dynamic keys not found in data"}

        all_data["MRData"][dynamic_key][inner_key] = []

        while offset < total:
            params = {"limit": limit, "offset": offset}
            paginated_data = get_data(endpoint, params, False)
            # logging.info(f"Received data with limit {limit} and offset {offset}")

            if paginated_data == "Exception request":
                logging.error("An error occurred while fetching paginated data.")
                break

            paginated_dynamic_data = (
                paginated_data.get("MRData").
                get(dynamic_key).
                get(inner_key)
            )

            all_data["MRData"][dynamic_key][inner_key].extend(paginated_dynamic_data)
            # logging.info(f"Appended {len(paginated_dynamic_data)} items from offset {offset}")
            offset += limit

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

# Retrieves resource data dynamically based on filters
def get_resource(resource_type, **filters):
    endpoint = build_endpoint(resource_type, **filters)
    return get_all_data(endpoint)

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

def get_dynamic_keys(data):
    dynamic_key = next((k for k in data.get("MRData", {}).keys() if k not in ["xmlns", "series", "url", "limit", "offset", "total"]), None)
    inner_key = None
    if dynamic_key:
        dynamic_value = data["MRData"].get(dynamic_key, {})
        if isinstance(dynamic_value, dict):
            inner_key = next(iter(dynamic_value.keys()), None)
    return dynamic_key, inner_key

def main():
    # Example 1: Get all circuits for the 2024 season
    circuits_2024 = get_resource(resource_type="circuits", season="2024")
    print(f"Example 1: {circuits_2024}")

    # Example 2: Get constructors for the first round of 2024
    constructors_round_1 = get_resource(resource_type="constructors", season="2024", round="1")
    print(f"Example 2: {constructors_round_1}")

    # Example 3: Get lap data for the 10th lap of the 2023 Monaco Grand Prix
    laps_monaco = get_resource(resource_type="laps", season="2023", round="6", laps="10")
    print(f"Example 3: {laps_monaco}")

    # Example 4: Get pitstops for the 4th stop of the 2019 Azerbaijan Grand Prix
    pitstops_azerbaijan = get_resource(resource_type="pitstops", season="2019", round="4", pitstops="4")
    print(f"Example 4: {pitstops_azerbaijan}")

    # Example 5: Get driver standings for the 2024 season
    driver_standings_2024 = get_resource(resource_type="driverstandings", season="2024")
    print(f"Example 5: {driver_standings_2024}")

    # Example 6: Get results for Max Verstappen in the 2021 season
    verstappen_results = get_resource(resource_type="results", season="2021", drivers_id="max_verstappen")
    print(f"Example 6: {verstappen_results}")

    # Example 7: Combine filters to get specific qualifying results
    qualifying_results = get_resource(
        resource_type="qualifying",
        season="2024",
        round="17",
        circuits_id="baku",
        drivers_id="leclerc"
    )
    print(f"Example 7: {qualifying_results}")

    # Example 8: Get constructors in position 1 for the 2020 season
    constructor_position_1 = get_resource(resource_type="constructorstandings", season="2020", position="1")
    print(f"Example 8: {constructor_position_1}")

    # Example 9: Get seasons featuring a specific status ID (e.g., statusId=2)
    seasons_status_2 = get_resource(resource_type="seasons", status_id="2")
    print(f"Example 9: {seasons_status_2}")



if __name__ == "__main__":
    main()