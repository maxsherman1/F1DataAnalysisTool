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

def get_circuits(
    season: str = None,
    round: str = None,
    circuit_id: str = None,
    constructor_id: str = None,
    driver_id: str = None,
    fastest_lap_rank: str = None,
    grid_position: str = None,
    finish_position: str = None,
    status_id: str = None
):
    endpoint_parts = []
    if season:
        endpoint_parts.append(season)
        if round:
            endpoint_parts.append(round)

    if circuit_id:
        endpoint_parts.extend(["circuits", circuit_id])
    else:
        if constructor_id:
            endpoint_parts.extend(["constructors", constructor_id])
        if driver_id:
            endpoint_parts.extend(["drivers", driver_id])
        if fastest_lap_rank:
            endpoint_parts.extend(["fastest", fastest_lap_rank])
        if grid_position:
            endpoint_parts.extend(["grid", grid_position])
        if finish_position:
            endpoint_parts.extend(["results", finish_position])
        if status_id:
            endpoint_parts.extend(["status", status_id])
        endpoint_parts.append("circuits")

    endpoint = "/".join(endpoint_parts)
    return get_all_data(endpoint)

def get_constructors():
    return get_all_data("constructors")

def get_constructor_standings(season: str):
    endpoint = f"{season}/constructorstandings"
    return get_all_data(endpoint)

def get_drivers():
    return get_all_data("drivers")


def get_driver_standings(season: str):
    endpoint = f"{season}/driverstandings"
    return get_all_data(endpoint)


def get_laps(season: str, round_number: int):
    endpoint = f"{season}/{round_number}/laps"
    return get_all_data(endpoint)


def get_pitstops(season: str, round_number: int):
    endpoint = f"{season}/{round_number}/pitstops"
    return get_all_data(endpoint)


def get_qualifying(season: str, round_number: int):
    endpoint = f"{season}/{round_number}/qualifying"
    return get_all_data(endpoint)


def get_races():
    return get_all_data("races")


def get_results(season: str, round_number: int):
    endpoint = f"{season}/{round_number}/results"
    return get_all_data(endpoint)


def get_seasons():
    return get_all_data("seasons")


def get_sprint():
    return get_all_data("sprint")


def get_status():
    return get_all_data("status")


def main():
    # Example 1: Fetch all circuits for the 2024 season
    circuits_2024 = get_circuits(season="2024")
    print(f"Example 1: {circuits_2024}")

    # Example 2: Fetch all circuits for the first round of the 2024 season
    circuits_round_1 = get_circuits(season="2024", round="1")
    print(f"Example 2: {circuits_round_1}")

    # Example 3: Fetch details of a specific circuit by circuitId
    circuit_albert_park = get_circuits(circuit_id="albert_park")
    print(f"Example 3: {circuit_albert_park}")

    # Example 4: Fetch all circuits a specific constructor has raced at
    circuits_mercedes = get_circuits(constructor_id="mercedes")
    print(f"Example 4: {circuits_mercedes}")

    # Example 5: Fetch all circuits a specific driver has raced at
    circuits_hamilton = get_circuits(driver_id="hamilton")
    print(f"Example 5: {circuits_hamilton}")

    # Example 6: Fetch circuits where a driver completed a lap ranked at position 24
    circuits_fastest_24 = get_circuits(fastest_lap_rank="24")
    print(f"Example 6: {circuits_fastest_24}")

    # Example 7: Fetch circuits where a specific grid position (e.g., 29) was used
    circuits_grid_29 = get_circuits(grid_position="29")
    print(f"Example 7: {circuits_grid_29}")

    # Example 8: Fetch circuits where a race finished with a driver in a specific position
    circuits_results_1 = get_circuits(finish_position="1")
    print(f"Example 8: {circuits_results_1}")

    # Example 9: Fetch circuits where a race ended with a specific status
    circuits_status_2 = get_circuits(status_id="2")
    print(f"Example 9: {circuits_status_2}")

    # Example 10: Combine filters (e.g., circuits for a specific season and round)
    circuits_season_round = get_circuits(season="2023", round="last")
    print(f"Example 10: {circuits_season_round}")

    # Example 11: Combine filters (e.g., circuits for a specific driver and constructor)
    circuits_driver_constructor = get_circuits(driver_id="verstappen", constructor_id="red_bull")
    print(f"Example 11: {circuits_driver_constructor}")

    # Example 12: Combine filters with status and grid position
    circuits_status_grid = get_circuits(status_id="1", grid_position="10")
    print(f"Example 12: {circuits_status_grid}")

    # Example 13: Combine all filters for maximum specificity
    circuits_all_filters = get_circuits(
        season="2022",
        round="5",
        circuit_id="monaco",
        constructor_id="ferrari",
        driver_id="leclerc",
        fastest_lap_rank="1",
        grid_position="1",
        finish_position="1",
        status_id="1"
    )
    print(f"Example 13: {circuits_all_filters}")


if __name__ == "__main__":
    main()