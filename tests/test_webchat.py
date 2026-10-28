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

import concurrent.futures
import pytest
from webchat import infer_location, parse_table_coordinates, parse_distance_table, extract_map_coords, create_map_html

def run_concurrently(func, *args, max_workers=10, iterations=50):
    expected = func(*args)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(func, *args) for _ in range(iterations)]
        for f in concurrent.futures.as_completed(futures):
            assert f.result() == expected

def test_infer_location_concurrent():
    run_concurrently(infer_location, "show me a map for New York")

@pytest.mark.xfail(raises=AssertionError, reason="folium generates random map IDs on each call, so results differ")
def test_create_map_html_concurrent():
    run_concurrently(create_map_html, [(48.8, 2.3), (51.5, -0.1)])

def test_parse_table_coordinates_concurrent():
    run_concurrently(parse_table_coordinates, "| Lat | Lon |\n|---|---|\n| 48.8 | 2.3 |\n", 0, 1)

def test_parse_distance_table_concurrent():
    run_concurrently(parse_distance_table, "| Lat1 | Lon1 | Lat2 | Lon2 |\n|---|---|---|---|\n| 48.8 | 2.3 | 51.5 | -0.1 |")

def test_extract_map_coords_concurrent():
    run_concurrently(extract_map_coords, "distance", "| Lat1 | Lon1 | Lat2 | Lon2 |\n|---|---|---|---|\n| 48.8 | 2.3 | 51.5 | -0.1 |")
