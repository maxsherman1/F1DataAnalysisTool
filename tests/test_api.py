import pytest
from api import json_handler
from api.jolpica_api import JolpicaAPI

@pytest.mark.parametrize("resource_type, filters", [
    ("circuits", {"season": "2024"}),
    ("circuits", {"constructors": "mercedes"}),
    ("circuits", {}),
    ("constructors", {"season": "2024", "round": "1"}),
    ("constructors", {}),
    ("drivers", {}),
    ("driverStandings", {"season": "2023"}),
    ("results", {"season": "2021", "drivers": "max_verstappen"}),
    ("pitstops", {"season": "2019", "round": "4", "pitstops": "2"}),
    ("qualifying", {"season": "2024", "round": "5", "drivers": "leclerc"}),
    ("qualifying", {"season": "2024", "round": "5"}),
    ("qualifying", {}),
    ("constructorStandings", {"season": "2020"}),
    ("laps", {"season": "2023", "round": "6"}),
    ("races", {}),
    ("results", {}),
    ("seasons", {}),
    ("sprint", {}),
    ("status", {"status": "2"}),
    ("status", {})
])
def test_data_retrieval(resource_type, filters):
    # Get data retrieval class instance
    api = JolpicaAPI(resource_type=resource_type, filters=filters)

    # Get all data, total number of data entries, inner data length
    data = api.get_all_data()
    total = data["MRData"]["total"]
    inner_key_path = json_handler.get_inner_key_path(data, resource_type)
    inner_data = json_handler.get_inner_data(data, inner_key_path)
    length_inner_data = len(inner_data) if inner_data else 0

    # Get cleaned data
    cleaned_data = api.get_cleaned_data()

    print()
    print(f"Total data entries on Jolpica API: {total}")
    print(f"Inner data entries retrieved from API: {length_inner_data}")
    print(f"Cleaned data entries retrieved from API: {cleaned_data.shape[0]}")

    if resource_type != "laps":
        assert str(length_inner_data) == total
        assert cleaned_data.shape[0] == length_inner_data
    else:
        assert str(cleaned_data.shape[0]) == total