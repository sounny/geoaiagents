import pytest
from webchat import extract_map_coords

def test_extract_map_coords_reverse_geocode_coordinates():
    table = "| Latitude | Longitude | Address |\n| --- | --- | --- |\n| 1.5 | 2.5 | Somewhere |"
    assert extract_map_coords('reverse_geocode_coordinates', table) == [(1.5, 2.5)]

def test_extract_map_coords_load_csv():
    table = "| Latitude | Longitude |\n| --- | --- |\n| -33.9 | 151.2 |"
    assert extract_map_coords('load_csv', table) == [(-33.9, 151.2)]
