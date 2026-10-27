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

import signal

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Timeout!")

@pytest.mark.xfail(raises=ValueError, strict=True, reason="create_map_html with deeply nested list causes ValueError from folium.Map location arg")
def test_create_map_html_deep_list():
    l = []
    for _ in range(200):
        l = [l]

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(2)
    try:
        create_map_html(l)
    finally:
        signal.alarm(0)

@pytest.mark.xfail(raises=KeyError, strict=True, reason="create_map_html with deeply nested dict causes KeyError from list destructuring")
def test_create_map_html_deep_dict():
    d = {}
    for _ in range(200):
        d = {"k": d}

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(2)
    try:
        create_map_html(d)
    finally:
        signal.alarm(0)

@pytest.mark.xfail(raises=ValueError, strict=True, reason="create_map_html with self-referential list causes ValueError from folium.Map location arg")
def test_create_map_html_self_ref_list():
    self_ref = []
    self_ref.append(self_ref)

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(2)
    try:
        create_map_html(self_ref)
    finally:
        signal.alarm(0)
