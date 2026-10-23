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

from unittest.mock import MagicMock
import math

def test_create_map_html_numeric_edge_cases(mocker):
    mock_map_instance = MagicMock()
    mock_map_instance._repr_html_.return_value = "<div>Mocked Map</div>"
    # Need to mock the Map so it raises ValueError when location contains NaNs,
    # as the real folium.Map does.
    def map_side_effect(location, *args, **kwargs):
        if any(math.isnan(x) for x in location):
            raise ValueError('Location values cannot contain NaNs.')
        return mock_map_instance

    mocker.patch("webchat.folium.Map", side_effect=map_side_effect)

    mock_marker_instance = MagicMock()
    def marker_side_effect(location, *args, **kwargs):
        if any(math.isnan(x) for x in location):
            raise ValueError('Location values cannot contain NaNs.')
        return mock_marker_instance

    mocker.patch("webchat.folium.Marker", side_effect=marker_side_effect)

    assert create_map_html([(0.0, 0.0)]) == "<div>Mocked Map</div>"
    assert create_map_html([(-1.0, -1.0)]) == "<div>Mocked Map</div>"
    assert create_map_html([(float("inf"), float("-inf"))]) == "<div>Mocked Map</div>"
    assert create_map_html([(10**20, -10**20)]) == "<div>Mocked Map</div>"

    with pytest.raises(ValueError, match="Location values cannot contain NaNs"):
        create_map_html([(float("nan"), float("nan"))])

def test_parse_distance_table_numeric_edge_cases():
    # 0.0
    table_0 = "| Lat1 | Lon1 | Lat2 | Lon2 |\n|---|---|---|---|\n| 0 | 0 | 0 | 0 |"
    assert parse_distance_table(table_0) == [(0.0, 0.0), (0.0, 0.0)]

    # negative numbers
    table_neg = "| Lat1 | Lon1 | Lat2 | Lon2 |\n|---|---|---|---|\n| -1 | -1 | -1 | -1 |"
    assert parse_distance_table(table_neg) == [(-1.0, -1.0), (-1.0, -1.0)]

    # inf
    table_inf = "| Lat1 | Lon1 | Lat2 | Lon2 |\n|---|---|---|---|\n| inf | -inf | inf | -inf |"
    assert parse_distance_table(table_inf) == [(float("inf"), float("-inf")), (float("inf"), float("-inf"))]

    # large integers
    table_large = ("| Lat1 | Lon1 | Lat2 | Lon2 |\n|---|---|---|---|\n"
                 "| 100000000000000000000 | 100000000000000000000 | 100000000000000000000 | 100000000000000000000 |")
    assert parse_distance_table(table_large) == [(10**20, 10**20), (10**20, 10**20)]

    # nan
    table_nan = "| Lat1 | Lon1 | Lat2 | Lon2 |\n|---|---|---|---|\n| nan | nan | nan | nan |"
    res_nan = parse_distance_table(table_nan)
    assert len(res_nan) == 2
    for p1, p2 in res_nan:
        assert math.isnan(p1) and math.isnan(p2)

def test_parse_table_coordinates_numeric_edge_cases():
    table = "| A | B | C |\n|---|---|---|\n| 0 | -1 | 100000000000000000000 |\n| nan | inf | -inf |"

    # 0 as index
    res_0 = parse_table_coordinates(table, 0, 0)
    assert res_0[0] == (0.0, 0.0)
    assert math.isnan(res_0[1][0]) and math.isnan(res_0[1][1])

    # negative numbers as index
    res_neg = parse_table_coordinates(table, -1, -2)
    assert res_neg[0] == (10**20, -1.0)
    assert res_neg[1] == (float("-inf"), float("inf"))

    # inf as index
    # Note: max(inf, -inf) is inf. len(cells) <= inf is True.
    # Therefore, it hits `continue` and never reaches the index access, returning [] instead of TypeError.
    res_inf = parse_table_coordinates(table, float("inf"), float("-inf"))
    assert res_inf == []

    # large integers as index
    res_large = parse_table_coordinates(table, 10**20, 10**20)
    assert res_large == []

    # nan as index
    # Note: max(nan, nan) is nan. len(cells) <= nan is False.
    # Therefore, it proceeds to index access `cells[float('nan')]` and raises TypeError.
    with pytest.raises(TypeError, match="list indices must be integers or slices, not float"):
        parse_table_coordinates(table, float("nan"), float("nan"))
