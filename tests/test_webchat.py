import pytest
from webchat import parse_distance_table

def test_parse_distance_table_locking_header_only_empty():
    assert parse_distance_table('| A | B | C | D |\n|---|---|---|---|') == []

    table = '| Lat1 | Lon1 | Lat2 | Lon2 |\n|---|---|---|---|\n| 48.8 | 2.3 | 51.5 | -0.1 |'
    assert parse_distance_table(table) == [(48.8, 2.3), (51.5, -0.1)]

from webchat import parse_table_coordinates, create_map_html
import re

def test_create_map_html_markers_and_skips_invalid_locking_markers():
    table = """| Location | Latitude | Longitude |
|---|---|---|
| Valid 1 | 51.5074 | -0.1278 |
| Invalid 1 | ABC | DEF |
| Valid 2 | 48.8566 | 2.3522 |
| Invalid 2 | 10.0 |"""
    points = parse_table_coordinates(table, 1, 2)
    assert len(points) == 2
    html = create_map_html(points)
    assert len(re.findall(r"L\.marker", html)) == 2

def test_create_map_html_boolean_equivalence():
    html_1 = create_map_html([(1.0, 0.0)])
    html_bool = create_map_html([(True, False)])
    assert re.sub(r'[a-z0-9]{32}', 'ID', html_1) == re.sub(r'[a-z0-9]{32}', 'ID', html_bool)

@pytest.mark.xfail(raises=AssertionError, strict=True, reason="Folium output retains -0.0, causing strict string inequality")
def test_create_map_html_neg0_equivalence():
    html_0 = create_map_html([(0.0, 0.0)])
    html_neg0 = create_map_html([(-0.0, -0.0)])
    assert re.sub(r'[a-z0-9]{32}', 'ID', html_0) == re.sub(r'[a-z0-9]{32}', 'ID', html_neg0)

def test_parse_table_coordinates_boolean_equivalence():
    table = "| Lat | Lon |\n|---|---|\n| 51.5 | -0.1 |"
    assert parse_table_coordinates(table, 0, 1) == parse_table_coordinates(table, False, True)

@pytest.mark.xfail(raises=TypeError, strict=True, reason="Floats not allowed for indexing")
def test_parse_table_coordinates_float_0_equivalence():
    table = "| Lat | Lon |\n|---|---|\n| 51.5 | -0.1 |"
    parse_table_coordinates(table, 0.0, 1.0)

@pytest.mark.xfail(raises=TypeError, strict=True, reason="Floats not allowed for indexing")
def test_parse_table_coordinates_float_neg0_equivalence():
    table = "| Lat | Lon |\n|---|---|\n| 51.5 | -0.1 |"
    parse_table_coordinates(table, -0.0, 1.0)
