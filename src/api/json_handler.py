from typing import Dict, Any, List, Optional

# Returns the path of the inner data (the actual data)
def get_inner_key_path(data: Dict[str, Any], resource_type: str) -> Optional[List[str]]:
    def search_inner_keys(nested: Any, target: str, path: Optional[List[str]] = None) -> Optional[List[str]]:
        path = path or []

        # Resource type input filtering
        if target.lower() in {"results", "qualifying"}:
            target = "Races"

        # if the provided dictionary is not a dictionary nor list, return None
        if not isinstance(nested, (dict, list)):
            print(f"Target {target} not found in current path: {path}")
            return None

        # If the argument is a list, retrieve the first value (will always be a dictionary)
        if isinstance(nested, list):
            nested = nested[0] if nested else None

        # get the key of the last entry of the dictionary
        last_key = next(reversed(nested), None) if nested else None

        # Check if the target has been found
        if last_key and last_key.lower() == target.lower():
            return path + [last_key]

        return search_inner_keys(nested.get(last_key, {}), target, path + [last_key])
    return search_inner_keys(data.get("MRData", {}), resource_type)

# Set the inner data and return the common data structure
def set_inner_data(data: Dict[str, Any], inner_key_path: List[str], inner_data: Any) -> Dict[str, Any]:
    # Retrieve second to last inner data
    old_inner_data = get_inner_data(data, inner_key_path, return_parent=True)

    # Get last key
    last_key = inner_key_path[-1]
    if isinstance(old_inner_data, list):
        old_inner_data = old_inner_data[0] # Handles lists if present
    # If last key is in inner data, replace it with the inner data
    if last_key in old_inner_data.keys():
        old_inner_data[last_key] = inner_data

    # Return the data
    return data

# find the inner data and returns it
def get_inner_data(data: Dict[str, Any], inner_key_path: List[str], return_parent: bool = False) -> List:
    # Retrieve initial inner data
    inner_data = data["MRData"]
    x = -1 if return_parent else len(inner_key_path)

    # Loop through the path list until the final value has been found
    for key in inner_key_path[:x]:
        if isinstance(inner_data, list):
            inner_data = inner_data[0]
        inner_data = inner_data[key]

    # Return inner data
    return inner_data

# Extend the inner data with additional provided data
def extend_inner_data(data: List, additional_data: List) -> List:

    # Data validation
    if not isinstance(data, list) or not isinstance(additional_data, list):
        raise TypeError(f"Both data arguments must be lists for appending.")

    # Handles empty arguments
    if not data or not additional_data:
        return data + additional_data

    # Retrieve the entries that required concatenating
    last_inner_entry = data[-1]
    first_additional_entry = additional_data[0]

    # Find the keys present in both entries
    common_keys = set(last_inner_entry.keys()) & set(first_additional_entry.keys())

    # if there are no common keys, which means the data is different, extend and return the data
    if not common_keys:
        data.extend(additional_data)
        return data

    # Identify the common data entries
    common_data_found = any(last_inner_entry[key] == first_additional_entry[key] for key in common_keys)

    # If there are no common data entries, no merging is necessary so extend and return the data
    if not common_data_found:
        data.extend(additional_data)
        return data

    # Identify the keys containing unique data values
    unique_data_keys = {key for key in common_keys if last_inner_entry[key] != first_additional_entry[key]}

    # For each unique key, append the unique data dynamically
    for key in unique_data_keys:
        existing_values = {tuple(sorted(item.items())) for item in last_inner_entry[key]}
        new_values = [item for item in first_additional_entry[key] if tuple(sorted(item.items())) not in existing_values]
        last_inner_entry[key].extend(new_values)

    # Skip the first additional entry
    additional_data = additional_data[1:]

    # Extend and return the additional data
    data.extend(additional_data) if additional_data else None
    return data