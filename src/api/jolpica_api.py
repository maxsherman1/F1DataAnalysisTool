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

# Retrieves data from the Jolpica-F1 API
def get_data(endpoint, params={"limit": 30, "offset": 0}, use_cache=True):

    # Add enpoint onto base url
    url = f"{BASE_URL}{endpoint}"

    # Extract parameters
    limit = params.get("limit")
    offset = params.get("offset")

    # Cache file name
    file_name = f"{endpoint.replace('/', '_')}_{limit}_{offset}.json"

    if use_cache and file_name in os.listdir(CACHE_DIR):
        return load_cache(file_name)

    # Make API call
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if use_cache:
            cache_data(file_name, data)
        return data

    except requests.exceptions.RequestException as e:
        logging.error(f"Error retrieving data: \n{e}")
        return "Exception request"


def cache_data(file_name, data):
    cache_file = f"{CACHE_DIR}/{file_name}"
    with open(cache_file, "w") as f:
        json.dump(data, f)
    logging.info(f"Data cached to {file_name} successfully.")

def load_cache(file_name):
    cache_file = f"{CACHE_DIR}/{file_name}"
    with open(cache_file, "r") as f:
        logging.info(f"Data loaded from {file_name} successfully.")
        return json.load(f)



def main():
    data = get_data("constructors")
    #for key in data:
    #    for x in data[key]:
    #        print(x)
        #print(key, ":", data[key])
    #print(data.get("MRData").get("total"))
    #print(get_all_data("constructors"))

if __name__ == "__main__":
    main()