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

from webchat import infer_location, parse_distance_table, parse_table_coordinates, create_map_html, respond
import pytest
from unittest.mock import MagicMock

def test_webchat_large_inputs(mocker):
    # Test infer_location with a very long string
    long_string = "for " + "a" * 1000000
    assert infer_location(long_string) == "a" * 1000000

    # Test parse_table_coordinates with a large table
    large_table_coords = "| Location | Lat | Lon |\n|---|---|---|\n" + "| Place | 10.0 | 20.0 |\n" * 10000
    res_coords = parse_table_coordinates(large_table_coords, 1, 2)
    assert len(res_coords) == 10000
    assert res_coords[0] == (10.0, 20.0)

    # Test parse_distance_table with a large table
    large_table_dist = "| Lat1 | Lon1 | Lat2 | Lon2 |\n|---|---|---|---|\n" + "| 10.0 | 20.0 | 30.0 | 40.0 |\n" * 10000
    res_dist = parse_distance_table(large_table_dist)
    assert len(res_dist) == 20000
    assert res_dist[0] == (10.0, 20.0)
    assert res_dist[1] == (30.0, 40.0)

    # Test create_map_html with a large number of coordinates (1000)
    large_points = [(10.0, 20.0)] * 1000
    mocker.patch('folium.Map._repr_html_', return_value="<html>mocked map</html>")
    html_res = create_map_html(large_points)
    assert html_res == "<html>mocked map</html>"

    # Test respond with large history and inputs
    msg = MagicMock(content="mock reply", function_call=None)
    mocker.patch('webchat.call_llm_with_retry', return_value=MagicMock(choices=[MagicMock(message=msg)]))

    large_history = [{"role": "user", "content": "hello"} for _ in range(1000)]
    large_message = "b" * 100000

    reply, map_html, logs, table = respond(large_message, large_history)
    assert reply == "mock reply"
