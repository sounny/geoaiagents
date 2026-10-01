import pytest
from webchat import extract_map_coords

def test_extract_map_coords_not_registered_tool():
    assert extract_map_coords('not_registered_tool', '| a |\n|---|\n| 1 |') == []

def test_extract_map_coords_convert_dd_to_dms():
    table = '| Latitude (DD) | Longitude (DD) | x |\n| --- | --- | --- |\n| 48.8 | 2.3 | z |'
    assert extract_map_coords('convert_dd_to_dms', table) == [(48.8, 2.3)]
