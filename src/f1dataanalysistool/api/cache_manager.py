import json
import logging
from typing import Dict, Any
from pathlib import Path

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Cache data function (does not check if cache folder is present)
def cache_data(file_path: Path, data: Dict[str, Any]) -> None:
    with open(file_path, "w") as f:
        json.dump(data, f)
    logging.info(f"Data cached to {file_path} successfully.")

# Load data function (does not check if cache file is present)
def load_cache(file_path: Path) -> Dict[str, Any]:
    with file_path.open("r") as f:
        logging.info(f"Data loaded from {file_path} successfully.")
        return json.load(f)

# Checks if cache file is in the cache directory
def is_cached(file_path: Path) -> bool:
    return file_path.exists()