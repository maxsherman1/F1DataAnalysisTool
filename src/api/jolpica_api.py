import json
import logging
import requests
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# The base URL for the API
BASE_URL = "https://api.jolpi.ca/ergast/f1/"

CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "data/cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Retrieves data from the Jolpica-F1 API
def get_data(endpoint, params=None, use_cache=True):

    # Add enpoint onto base url
    url = f"{BASE_URL}{endpoint}.json"

    # Extract parameters
    limit = params.get("limit")
    offset = params.get("offset")

    # Cache file name
    cache_file = CACHE_DIR / f"{endpoint.replace('/', '_')}_{limit}_{offset}.json"

    # Make API call
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if use_cache:
            cache_data(cache_file, data)
        logging.info(f"Data from {url} successfully retrieved and cached.")
        return data

    except requests.exceptions.RequestException as e:
        logging.error(f"Error retrieving data: \n{e}")
        return "Exception request"


def cache_data(cache_file, data):
    with open(cache_file, "w") as f:
        json.dump(data, f)

def main():
    data = get_data("constructors", {"limit": 10, "offset": 0})
    for key in data:
        for x in data[key]:
            print(x)
        #print(key, ":", data[key])

if __name__ == "__main__":
    main()