import pytest
from webchat import parse_distance_table, extract_map_coords

def test_parse_distance_table_header_only():
    table = "| Lat1 | Lon1 | Lat2 | Lon2 |\n|---|---|---|---|"
    result = parse_distance_table(table)
    assert result == []

def test_parse_distance_table_non_numeric():
    table = "| Lat1 | Lon1 | Lat2 | Lon2 |\n|---|---|---|---|\n| a | b | c | d |\n| 10.0 | 20.0 | 30.0 | 40.0 |"
    result = parse_distance_table(table)
    assert result == [(10.0, 20.0), (30.0, 40.0)]

def test_parse_distance_table_valid():
    table = "| Lat1 | Lon1 | Lat2 | Lon2 |\n|---|---|---|---|\n| 10.0 | 20.0 | 30.0 | 40.0 |\n| 50.0 | 60.0 | 70.0 | 80.0 |"
    result = parse_distance_table(table)
    assert result == [(10.0, 20.0), (30.0, 40.0), (50.0, 60.0), (70.0, 80.0)]

def test_extract_map_coords_unknown_tool():
    result = extract_map_coords("unknown_tool", "table content")
    assert result == []

def test_extract_map_coords_distance_tool():
    table = "| Lat1 | Lon1 | Lat2 | Lon2 |\n|---|---|---|---|\n| 10.0 | 20.0 | 30.0 | 40.0 |"
    result = extract_map_coords("calculate_distance", table)
    assert result == [(10.0, 20.0), (30.0, 40.0)]

def test_extract_map_coords_default_tool():
    # geocode_locations uses (2, 3) which means 3rd and 4th column are lat, lon
    table = "| Query | Matched | Lat | Lon |\n|---|---|---|---|\n| Paris | Paris, France | 48.8566 | 2.3522 |"
    result = extract_map_coords("geocode_locations", table)
    assert result == [(48.8566, 2.3522)]
