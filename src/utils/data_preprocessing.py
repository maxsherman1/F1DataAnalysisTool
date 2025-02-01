import logging
import json
import sys
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List

sys.path.append(str(Path(__file__).resolve().parent.parent))

from api.jolpica_api import get_inner_data, get_all_data, get_inner_key_path


# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define cache and processed directories
PROCESSED_DIR = Path(__file__).resolve().parent.parent.parent / "data/processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)  # Ensure the processed directory exists


def convert_to_dataframe(data: List) -> pd.DataFrame:
    if not data:
        logging.warning("No data provided for conversion to DataFrame. Returning empty DataFrame.")
        return pd.DataFrame()

    try:
        df = pd.DataFrame(data)
        logging.info("Converted data into DataFrame with shape %s", df.shape)
        return df
    except Exception as e:
        logging.error("Error converting data to DataFrame: %s", str(e))
        return pd.DataFrame()

def clean_data(resource_type, **filters) -> pd.DataFrame:
    data = get_all_data(resource_type, **filters)
    inner_key_path = get_inner_key_path(data, resource_type=resource_type)
    inner_data = get_inner_data(data, inner_key_path)
    df = convert_to_dataframe(inner_data)
    print(df)

def main():
    clean_data(resource_type="circuits", season="2024")

if __name__ == "__main__":
    main()