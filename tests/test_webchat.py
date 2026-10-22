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

import pytest
import re
from webchat import infer_location, create_map_html, parse_table_coordinates, parse_distance_table, extract_map_coords, respond, chat
from unittest.mock import patch, mock_open, MagicMock
from types import SimpleNamespace

# infer_location boundary tests
def test_infer_location_boundaries():
    assert infer_location("") is None
    assert infer_location("a") is None
    assert infer_location("for ") is None
    assert infer_location("for a") == "a"
    assert infer_location("for " + "a" * 10000) == "a" * 10000
    assert infer_location("for 東京") is None

# create_map_html boundary tests
def test_create_map_html_boundaries():
    assert create_map_html([]) == ""
    html = create_map_html([(0.0, 0.0)])
    assert "L.marker" in html

    # 10000 markers might be too slow for test, 1000 is okay for sensible size
    large_points = [(0.0, 0.0)] * 1000
    html_large = create_map_html(large_points)
    assert len(re.findall(r"L\.marker", html_large)) == 1000

# parse_table_coordinates boundary tests
def test_parse_table_coordinates_boundaries():
    assert parse_table_coordinates("", 1, 2) == []
    assert parse_table_coordinates("a", 1, 2) == []

    header = "| Location | Latitude | Longitude |\n|---|---|---|\n"
    assert parse_table_coordinates(header, 1, 2) == []

    unicode_table = header + "| 東京 | 35.6895 | 139.6917 |\n"
    assert parse_table_coordinates(unicode_table, 1, 2) == [(35.6895, 139.6917)]

    large_table = header + "| A | 0.0 | 0.0 |\n" * 1000
    assert len(parse_table_coordinates(large_table, 1, 2)) == 1000

# parse_distance_table boundary tests
def test_parse_distance_table_boundaries():
    assert parse_distance_table("") == []
    assert parse_distance_table("a") == []

    header = "| Lat1 | Lon1 | Lat2 | Lon2 |\n|---|---|---|---|\n"
    assert parse_distance_table(header) == []

    unicode_table = header + "| 0.0 | 0.0 | 1.0 | 1.0 | 東京 |\n"
    assert parse_distance_table(unicode_table) == [(0.0, 0.0), (1.0, 1.0)]

    large_table = header + "| 0.0 | 0.0 | 1.0 | 1.0 |\n" * 1000
    assert len(parse_distance_table(large_table)) == 2000

# extract_map_coords boundary tests
def test_extract_map_coords_boundaries():
    assert extract_map_coords("", "") == []
    assert extract_map_coords("a", "a") == []

    header_geocode = "| Query | Matched | Lat | Lon |\n|---|---|---|---|\n"
    assert extract_map_coords("geocode_locations", header_geocode) == []
    unicode_geocode = header_geocode + "| 東京 | 東京 | 35.6895 | 139.6917 |\n"
    assert extract_map_coords("geocode_locations", unicode_geocode) == [(35.6895, 139.6917)]

    large_geocode = header_geocode + "| A | A | 0.0 | 0.0 |\n" * 1000
    assert len(extract_map_coords("geocode_locations", large_geocode)) == 1000

# respond and chat boundary tests
@patch("webchat.call_llm_with_retry")
@patch("webchat.registry")
def test_respond_and_chat_boundaries(mock_registry, mock_call_llm):
    mock_registry.invoke.return_value = "| Query | Matched | Lat | Lon |\n|---|---|---|---|\n| a | a | 0.0 | 0.0 |"

    # Mock LLM response for first call (without function call)
    mock_message_1 = SimpleNamespace(content="Hello", function_call=None)
    mock_response_1 = SimpleNamespace(choices=[SimpleNamespace(message=mock_message_1)])

    # Mock LLM response for a function call
    mock_func_call = SimpleNamespace(name="geocode_locations", arguments='{"locations": "a"}')
    mock_message_2 = SimpleNamespace(content=None, function_call=mock_func_call)
    mock_response_2 = SimpleNamespace(choices=[SimpleNamespace(message=mock_message_2)])

    mock_call_llm.return_value = mock_response_1

    # Empty message
    reply, map_html, logs, table = respond("", [])
    assert reply == "Hello"

    # Message with 1 char
    reply, map_html, logs, table = respond("a", [])
    assert reply == "Hello"

    # Large message
    reply, map_html, logs, table = respond("a" * 1000, [])
    assert reply == "Hello"

    # Unicode message
    reply, map_html, logs, table = respond("東京", [])
    assert reply == "Hello"

    # Test chat function which wraps respond
    history, map_html, logs, table = chat("東京", [], None)
    assert len(history) == 2
    assert history[-1] == {"role": "assistant", "content": "Hello"}

    # Test with upload_file mock
    mock_file = MagicMock()
    mock_file.name = "test.txt"
    with patch("builtins.open", mock_open(read_data="dummy data")):
        reply, map_html, logs, table = respond("", [], upload_file=mock_file)
        assert reply == "Hello"

    # Test when infer_location matches (requires function call and second LLM call)
    mock_call_llm.side_effect = [mock_response_1, mock_response_1]
    reply, map_html, logs, table = respond("for a", [])
    assert reply == "Hello" # first response returns mock_response_1, infer location triggers geocode, second response returns mock_response_1 again
    mock_call_llm.side_effect = None # reset

    # Test function call directly from LLM
    mock_message_3 = SimpleNamespace(content="After tool", function_call=None)
    mock_response_3 = SimpleNamespace(choices=[SimpleNamespace(message=mock_message_3)])

    mock_call_llm.side_effect = [mock_response_2, mock_response_3]
    reply, map_html, logs, table = respond("use tool", [])
    assert reply == "After tool"
    mock_call_llm.side_effect = None
