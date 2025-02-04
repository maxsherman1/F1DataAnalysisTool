import logging
import pandas as pd
from pathlib import Path
from typing import List, Dict
from api.jolpica_api import JolpicaAPI

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define cache and processed directories
CLEANED_DIR = Path(__file__).resolve().parent.parent.parent / "data/cleaned"
CLEANED_DIR.mkdir(parents=True, exist_ok=True)  # Ensure the processed directory exists

# Converts the provided list to a pandas dataframe
def convert_to_dataframe(data: List) -> pd.DataFrame:
    # Checking for data
    if not data:
        logging.warning("No data provided for conversion to DataFrame. Returning empty DataFrame.")
        return pd.DataFrame()
    # Normalise JSON data
    try:
        return pd.json_normalize(data)
    # Log an error if the conversion fails
    except Exception as e:
        logging.error("Error converting data to DataFrame: %s", str(e))
        return pd.DataFrame()

# Save the dataframe to the file path
def save_data(data: pd.DataFrame, file_path: Path) -> None:
    # Check if there is data to save
    if data.empty:
        logging.warning("No data provided for saving.")
        return

    # Save data to csv at file_path
    try:
        data.to_csv(file_path, index=False)
        logging.info("Saved cleaned data to %s", file_path)
    # Log an error if saving fails
    except Exception as e:
        logging.error("Error saving cleaned data: %s", str(e))

# Retrieve, preprocess, convert, and save the data to csv
def convert_and_save_data(jolpica_api: JolpicaAPI) -> None:
    file_name = jolpica_api.get_cleaned_file_name()
    data = preprocess_data(jolpica_api.get_inner_data())
    save_data(convert_to_dataframe(data), CLEANED_DIR / file_name)

# Function that removes any nested dictionaries by flattening the inner data.
def preprocess_data(inner_data: List[Dict]) -> List[Dict]:

    # Function responsible for flattening the data
    def flatten(data: Dict) -> Dict:
        # Empty dictionary for updated data
        flattened_data = {}
        # Loop through the data for each entry in the dictionary
        for key, value in data.items():
            # Check for nested dictionaries
            if isinstance(value, list) and isinstance(value[0], dict):
                # Check the length of the nested dictionary
                if len(value) == 1:
                    # If length is 1, update the key with no index
                    for k, v in value[0].items():
                        flattened_data[f"{key}.{k}"] = v
                elif len(value) > 1:
                    # If length is greater than 1, include indexing in the new key
                    for idx, item in enumerate(value, start=1):
                        for k, v in item.items():
                            flattened_data[f"{key}.{idx}.{k}"] = v

            # If no nested dictionary found just update the data
            else:
                flattened_data[key] = value

        # Flattened data
        return flattened_data

    # Return the flattened data for each entry in inner data if inner data has been provided
    return [flatten(entry) for entry in inner_data] if inner_data else inner_data