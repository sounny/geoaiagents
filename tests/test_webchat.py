from unittest.mock import patch, MagicMock
from webchat import infer_location, extract_map_coords, respond, chat, parse_table_coordinates

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

@pytest.mark.xfail(raises=TypeError, strict=True, reason="bug: does not handle bytes properly")
def test_infer_location_bytes():
    infer_location(b"hello")

@pytest.mark.xfail(raises=TypeError, strict=True, reason="bug: does not handle bytes properly")
def test_parse_table_coords_bytes():
    parse_table_coordinates(b"line1\nline2\nline3", 1, 2)

@pytest.mark.xfail(raises=TypeError, strict=True, reason="bug: does not handle bytes properly")
def test_parse_distance_table_bytes():
    parse_distance_table(b"line1\nline2\nline3")

@pytest.mark.xfail(raises=TypeError, strict=True, reason="bug: does not handle bytes properly")
def test_extract_map_coords_bytes():
    extract_map_coords("calculate_distance", b"line1\nline2\nline3")

@pytest.mark.xfail(raises=TypeError, strict=True, reason="bug: does not handle bytes properly")
def test_respond_bytes():
    with patch("webchat.call_llm_with_retry") as mock_llm:
        mock_msg = MagicMock()
        mock_msg.function_call = None
        mock_msg.content = "reply"
        mock_llm.return_value.choices = [MagicMock(message=mock_msg)]
        respond(b"msg", [])

def test_chat_bytes():
    with patch("webchat.respond", return_value=("reply", "map", "logs", "table")):
        res = chat(b"hello", [], None)
        assert res == ([{'role': 'user', 'content': b'hello'}, {'role': 'assistant', 'content': 'reply'}], 'map', 'logs', 'table')
