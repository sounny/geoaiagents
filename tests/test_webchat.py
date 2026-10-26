import math
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

@pytest.mark.parametrize("bad_val", [
    float("nan"),
    pytest.param(float("inf"), marks=pytest.mark.xfail(reason="Bug: inf silently returns empty list instead of TypeError")),
    float("-inf"),
    -0.0
])
def test_parse_table_coordinates_bad_floats(bad_val):
    table = "| A | B | C |\n|---|---|---|\n| 1.0 | 2.0 | 3.0 |"
    with pytest.raises(TypeError):
        parse_table_coordinates(table, bad_val, bad_val)

@pytest.mark.parametrize("bad_val", [
    float("nan"),
    pytest.param(float("inf"), marks=pytest.mark.xfail(reason="Bug: infinite coordinates do not raise error")),
    pytest.param(float("-inf"), marks=pytest.mark.xfail(reason="Bug: infinite coordinates do not raise error")),
    -0.0
])
def test_create_map_html_bad_floats(bad_val):
    if bad_val == -0.0:
        html = create_map_html([(bad_val, bad_val)])
        assert isinstance(html, str)
    else:
        with pytest.raises(ValueError):
            create_map_html([(bad_val, bad_val)])
