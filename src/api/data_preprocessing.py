import logging
import pandas as pd
from pathlib import Path
from typing import List
from api.jolpica_api import JolpicaAPI

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define cache and processed directories
CLEANED_DIR = Path(__file__).resolve().parent.parent.parent / "data/cleaned"
CLEANED_DIR.mkdir(parents=True, exist_ok=True)  # Ensure the processed directory exists

# Converts the provided list to a pandas dataframe
def convert_to_dataframe(data: List) -> pd.DataFrame:
    if not data:
        logging.warning("No data provided for conversion to DataFrame. Returning empty DataFrame.")
        return pd.DataFrame()
    try:
        return pd.json_normalize(data)
    except Exception as e:
        logging.error("Error converting data to DataFrame: %s", str(e))
        return pd.DataFrame()

# Save the dataframe to the file path
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
    jolpica_api = JolpicaAPI(resource_type, **filters)
    data = convert_to_dataframe(jolpica_api.get_inner_data())
    file_name = f"{jolpica_api.build_endpoint().replace('/', '_')}_cleaned.csv"
    save_data(data=data, file_path=CLEANED_DIR / file_name)