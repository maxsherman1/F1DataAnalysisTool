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
    def flatten(data: Dict) -> List[Dict]:
        flattened_entries = []
        base_data = {k: v for k, v in data.items() if not isinstance(v, list) or not v or not isinstance(v[0], dict)}

        nested_lists = {k: v for k, v in data.items() if isinstance(v, list) and v and isinstance(v[0], dict)}

        if not nested_lists:
            return [base_data]

        for key, nested_dicts in nested_lists.items():
            for nested_dict in nested_dicts:
                new_entry = base_data.copy()
                for k, v in nested_dict.items():
                    new_entry[f"{key}.{k}"] = v
                flattened_entries.append(new_entry)

        return flattened_entries

    flattened_data = []
    for entry in inner_data:
        flattened_data.extend(flatten(entry))

    return flattened_data

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

def convert_to_ms(df: pd.DataFrame, column: List = None) -> pd.DataFrame:
    def time_to_ms(time):
        try:
            if isinstance(time, (int, float)):
                return int(time * 1000)
            if isinstance(time, str):
                if ":" not in time:
                    return int(float(time) * 1000)
                time_parts = time.split(":")
                if len(time_parts) == 2:
                    minutes, rest = time_parts
                    return (int(minutes) * 60000) + int(float(rest) * 1000)
            return time
        except (ValueError, TypeError):
            logging.warning(f"Invalid time format: {time}")

    try:
        if column is None:
            for col in get_columns(df):
                if any(part in ["time", "duration", "Q1", "Q2", "Q3"] for part in col.split(".")):
                    df[col] = df[col].apply(time_to_ms)
            logging.info("Time values converted to milliseconds in all time or duration columns.")
        else:
            for col in column:
                df[col] = df[col].apply(time_to_ms)
    except Exception as e:
        logging.error(f"Error converting time to milliseconds: {e}")
    return df

def convert_to_numeric(df: pd.DataFrame) -> pd.DataFrame:
    for col in get_columns(df):
        if not pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].apply(lambda x: pd.to_numeric(x, errors="ignore"))
    logging.info("Converted applicable columns to numeric values.")
    return df