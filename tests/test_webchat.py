import pytest
from webchat import parse_table_coordinates

def test_parse_table_coordinates():
    table = "| Latitude | Longitude |\n|---|---|\n| 48.8566 | 2.3522 |\n| 51.5074 | -0.1278 |"
    coords = parse_table_coordinates(table, lat_index=0, lon_index=1)
    assert coords == [(48.8566, 2.3522), (51.5074, -0.1278)]

def test_parse_table_coordinates_ignores_non_numeric():
    table = "| Latitude | Longitude |\n|---|---|\n| 48.8566 | 2.3522 |\n| 51.5074 | invalid |\n| foo | 12.34 |"
    coords = parse_table_coordinates(table, lat_index=0, lon_index=1)
    assert coords == [(48.8566, 2.3522)]
