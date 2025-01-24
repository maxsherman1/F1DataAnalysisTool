import logging
import requests

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# The base URL for the API
BASE_URL = "https://api.jolpi.ca/ergast/f1/"

# Retrieves data from the Jolpica-F1 API
def get_data(endpoint, params=None):

    # Add enpoint onto base url
    url = f"{BASE_URL}{endpoint}"

    # Make API call
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data

    except requests.exceptions.RequestException as e:
        logging.error(f"Error retrieving data: \n{e}")
        return "Exception request"


def main():
    print(get_data("constructor.json", {"limit": 1, "offset": 0}))

if __name__ == "__main__":
    main()