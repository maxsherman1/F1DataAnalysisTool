import logging
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple

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
def save_to_csv(data: pd.DataFrame, file_name: str) -> None:
    # Check if there is data to save
    if data.empty:
        logging.warning("No data provided for saving.")
        return

    # Save data to csv
    file_path = CLEANED_DIR / file_name
    try:
        data.to_csv(file_path, index=False)
        logging.info("Saved cleaned data to %s", file_path)
    # Log an error if saving fails
    except Exception as e:
        logging.error("Error saving cleaned data: %s", str(e))

# Load data from the csv file
def load_from_csv(file_name: str) -> pd.DataFrame:
    file_path = CLEANED_DIR / file_name
    # Load from filepath
    try:
        data = pd.read_csv(file_path)
        logging.info("Loaded cleaned data from %s", file_path)
        return data
    # Log error if csv loading fails
    except Exception as e:
        logging.error("Error loading cleaned data from csv: %s", str(e))
        return pd.DataFrame()

# Checks if csv file is loaded
def is_loaded_csv(file_name: str) -> bool:
    file_path = CLEANED_DIR / file_name
    return file_path.exists()

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

def get_columns(df: pd.DataFrame) -> List[str]:
    return list(df.columns)

def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna()
    if df.empty:
        logging.warning("Dataframe is empty after removing missing values. Returning empty DataFrame.")
    return df

def get_column_min_max(df: pd.DataFrame, column: str) -> Tuple[float, float] | Tuple[None, None]:
    if pd.api.types.is_numeric_dtype(df[column]):
        return df[column].min(), df[column].max()
    return None, None

def convert_to_ms(df: pd.DataFrame, column: str) -> pd.DataFrame:
    def time_to_ms(time_str):
        time_parts = str(time_str).split(":")
        if len(time_parts) == 2:
            minutes, rest = time_parts
            seconds, milliseconds = rest.split(".") if "." in rest else (rest, "0")
            return (int(minutes) * 60000) + (int(seconds) * 1000) + int(milliseconds)
        return None

    try:
        df[column] = df[column].apply(time_to_ms)  # Convert to ms
        logging.info("Time values converted to milliseconds.")
    except Exception as e:
        logging.error(f"Error converting time to milliseconds: {e}")
    return df

