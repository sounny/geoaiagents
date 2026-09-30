import pytest
from webchat import extract_map_coords

def test_extract_map_coords_geocode_locations():
    table = "| Input | Matched Address | Latitude | Longitude |\n|---|---|---|---|\n| Paris | Paris FR | 48.8566 | 2.3522 |"
    result = extract_map_coords('geocode_locations', table)
    assert result == [(48.8566, 2.3522)]
