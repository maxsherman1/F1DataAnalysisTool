import logging
import sys
import pandas as pd
from pathlib import Path
from typing import List

sys.path.append(str(Path(__file__).resolve().parent.parent))

from api.jolpica_api import get_inner_data, get_all_data, get_inner_key_path, build_endpoint

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define cache and processed directories
CLEANED_DIR = Path(__file__).resolve().parent.parent.parent / "data/cleaned"
CLEANED_DIR.mkdir(parents=True, exist_ok=True)  # Ensure the processed directory exists

def convert_to_dataframe(data: List) -> pd.DataFrame:
    if not data:
        logging.warning("No data provided for conversion to DataFrame. Returning empty DataFrame.")
        return pd.DataFrame()

    try:
        return pd.DataFrame(data)
    except Exception as e:
        logging.error("Error converting data to DataFrame: %s", str(e))
        return pd.DataFrame()

def clean_data(resource_type: str, **filters) -> pd.DataFrame:
    data = get_all_data(resource_type, **filters)
    inner_key_path = get_inner_key_path(data, resource_type=resource_type)
    inner_data = get_inner_data(data, inner_key_path)
    return convert_to_dataframe(inner_data)

def save_data(data: pd.DataFrame, file_path: Path) -> None:
    if data.empty:
        logging.warning("No data provided for saving.")
        return

    try:
        data.to_csv(file_path, index=False)
        logging.info("Saved cleaned data to %s", file_path)
    except Exception as e:
        logging.error("Error saving cleaned data: %s", str(e))

def clean_and_save_data(resource_type:str, **filters):
    data = clean_data(resource_type, **filters)
    endpoint = build_endpoint(resource_type, **filters).replace('/', '_')
    save_data(data=data, file_path=CLEANED_DIR / f"{endpoint}_cleaned.csv")