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

def get_circuits():
    return get_all_data("circuits")

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
    # Example to retrieve all constructors
    try:
        # Example for a specific season (e.g., 2023)
        season = "2023"
        round_number = 1  # Example round for the 2023 season

        # Get all circuits
        logging.info("Retrieving circuits data...")
        all_circuits = get_circuits()
        total = all_circuits.get("MRData").get("total")
        logging.info(f"Retrieved {total} circuits.") if all_circuits else logging.error(
            "Failed to retrieve circuits data.")

        # Get all constructors
        logging.info("Retrieving constructors data...")
        all_constructors = get_constructors()
        total = all_constructors.get("MRData").get("total")
        logging.info(
            f"Retrieved {total} constructors.") if all_constructors else logging.error(
            "Failed to retrieve constructors data.")

        # Get constructor standings for a given season
        logging.info(f"Retrieving constructor standings for {season}...")
        constructor_standings = get_constructor_standings(season)
        total = constructor_standings.get("MRData").get("total")
        logging.info(
            f"Retrieved {total} constructor standings.") if constructor_standings else logging.error(
            f"Failed to retrieve constructor standings for {season}.")

        # Get all drivers
        logging.info("Retrieving drivers data...")
        all_drivers = get_drivers()
        total = all_drivers.get("MRData").get("total")
        logging.info(f"Retrieved {total} drivers.") if all_drivers else logging.error(
            "Failed to retrieve driver data.")

        # Get driver standings for a given season
        logging.info(f"Retrieving driver standings for {season}...")
        driver_standings = get_driver_standings(season)
        total = driver_standings.get("MRData").get("total")
        logging.info(
            f"Retrieved {total} driver standings.") if driver_standings else logging.error(
            f"Failed to retrieve driver standings for {season}.")

        # Get lap data for a specific season and round
        logging.info(f"Retrieving lap data for {season} round {round_number}...")
        laps = get_laps(season, round_number)
        total = laps.get("MRData").get("total")
        logging.info(
            f"Retrieved {total} laps for {season} round {round_number}.") if laps else logging.error(
            f"Failed to retrieve lap data for {season} round {round_number}.")

        # Get pitstop data for a specific season and round
        logging.info(f"Retrieving pitstops data for {season} round {round_number}...")
        pitstops = get_pitstops(season, round_number)
        total = pitstops.get("MRData").get("total")
        logging.info(
            f"Retrieved {total} pitstops for {season} round {round_number}.") if pitstops else logging.error(
            f"Failed to retrieve pitstops data for {season} round {round_number}.")

        # Get qualifying data for a specific season and round
        logging.info(f"Retrieving qualifying data for {season} round {round_number}...")
        qualifying = get_qualifying(season, round_number)
        total = qualifying.get("MRData").get("total")
        logging.info(
            f"Retrieved {total} qualifying results for {season} round {round_number}.") if qualifying else logging.error(
            f"Failed to retrieve qualifying data for {season} round {round_number}.")

        # Get all races
        logging.info("Retrieving races data...")
        all_races = get_races()
        total = all_races.get("MRData").get("total")
        logging.info(f"Retrieved {total} races.") if all_races else logging.error(
            "Failed to retrieve races data.")

        # Get results for a specific round
        logging.info(f"Retrieving results for {season} round {round_number}...")
        results = get_results(season, round_number)
        total = results.get("MRData").get("total")
        logging.info(
            f"Retrieved {total} results for {season} round {round_number}.") if results else logging.error(
            f"Failed to retrieve results for {season} round {round_number}.")

        # Get all seasons
        logging.info("Retrieving seasons data...")
        all_seasons = get_seasons()
        total = all_seasons.get("MRData").get("total")
        logging.info(f"Retrieved {total} seasons.") if all_seasons else logging.error(
            "Failed to retrieve seasons data.")

        # Get sprint data for a specific season and round
        logging.info(f"Retrieving sprint data...")
        sprint = get_sprint()
        total = sprint.get("MRData").get("total")
        logging.info(
            f"Retrieved {total} sprint results.") if sprint else logging.error(
            f"Failed to retrieve sprint data.")

        # Get status data
        logging.info("Retrieving status data...")
        status = get_status()
        total = status.get("MRData").get("total")
        logging.info(f"Retrieved {total} status entries.") if status else logging.error(
            "Failed to retrieve status data.")

        logging.info("All data retrieval completed.")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()