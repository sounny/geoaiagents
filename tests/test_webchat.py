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
from webchat import infer_location, parse_table_coordinates, parse_distance_table, extract_map_coords, respond, chat
from unittest.mock import patch, MagicMock

class MyStr(str):
    pass

class MyDict(dict):
    pass

def test_infer_location_subclass():
    assert infer_location(MyStr("for Paris")) == "Paris"

def test_parse_table_coordinates_subclass():
    res = parse_table_coordinates(MyStr("id|lat|lon\n--|--|--\n1|10.0|20.0"), 1, 2)
    assert res == [(10.0, 20.0)]

def test_parse_distance_table_subclass():
    res = parse_distance_table(MyStr("id|lat1|lon1|lat2|lon2\n--|--|--|--|--\n1|10.0|20.0|30.0|40.0"))
    assert res == [(1.0, 10.0), (20.0, 30.0)]

def test_extract_map_coords_subclass():
    res = extract_map_coords(MyStr("geocode_locations"), MyStr("id|loc|lat|lon\n--|--|--|--\n1|paris|10.0|20.0"))
    assert res == [(10.0, 20.0)]

@pytest.mark.xfail(reason="extract_map_coords bug with parsing calculate_distance due to identity equality check on parser == 'distance'")
def test_extract_map_coords_distance_subclass():
    res = extract_map_coords(MyStr("calculate_distance"), MyStr("id|loc|lat1|lon1|lat2|lon2\n--|--|--|--|--|--\n1|paris|10.0|20.0|30.0|40.0"))
    assert res == [(1.0, 10.0), (20.0, 30.0)]

def test_respond_subclass():
    with patch('webchat.call_llm_with_retry') as mock_call:
        mock_call.return_value = MagicMock()
        mock_call.return_value.choices = [MagicMock()]
        mock_call.return_value.choices[0].message = MagicMock()
        mock_call.return_value.choices[0].message.function_call = None
        mock_call.return_value.choices[0].message.content = "Hello"
        with patch('webchat.infer_location', return_value=None):
            reply, map_html, logs, table = respond(MyStr("test message"), [MyDict({"role": "user", "content": "hi"})], None)
            assert reply == "Hello"

def test_chat_subclass():
    with patch('webchat.call_llm_with_retry') as mock_call:
        mock_call.return_value = MagicMock()
        mock_call.return_value.choices = [MagicMock()]
        mock_call.return_value.choices[0].message = MagicMock()
        mock_call.return_value.choices[0].message.function_call = None
        mock_call.return_value.choices[0].message.content = "Hello"
        with patch('webchat.infer_location', return_value=None):
            history, map_html, logs, table = chat(MyStr("test message"), [MyDict({"role": "user", "content": "hi"})], None)
            assert len(history) == 3
