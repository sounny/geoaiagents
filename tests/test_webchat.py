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

def test_parse_table_coordinates_numpy():
    numpy = pytest.importorskip("numpy")
    table = "| Location | Latitude | Longitude |\n|---|---|---|\n| Valid 1 | 51.5074 | -0.1278 |"

    res_int = parse_table_coordinates(table, 1, 2)
    res_np = parse_table_coordinates(table, numpy.int64(1), numpy.int64(2))
    assert res_int == res_np

def test_create_map_html_numpy():
    numpy = pytest.importorskip("numpy")
    points_float = [(51.5, -0.1)]
    points_np = [(numpy.float64(51.5), numpy.float64(-0.1))]

    res_float = create_map_html(points_float)
    res_np = create_map_html(points_np)

    def normalize_html(html):
        return re.sub(r'[a-z0-9]{32}', 'ID', html)

    assert normalize_html(res_float) == normalize_html(res_np)
