import webchat
from unittest.mock import MagicMock
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

def test_infer_location_wrong_type():
    with pytest.raises(TypeError):
        webchat.infer_location(123)

def test_create_map_html_wrong_type():
    with pytest.raises(TypeError):
        webchat.create_map_html(123)

def test_parse_table_coordinates_wrong_type():
    with pytest.raises(AttributeError):
        webchat.parse_table_coordinates(123, 1, 2)

def test_parse_distance_table_wrong_type():
    with pytest.raises(AttributeError):
        webchat.parse_distance_table(123)

@pytest.mark.xfail(reason="silently ignores the wrong type")
def test_extract_map_coords_wrong_type():
    with pytest.raises(TypeError):
        webchat.extract_map_coords(123, 456)

def test_run_tool_wrong_type():
    with pytest.raises(AttributeError):
        webchat.run_tool(123)

def test_respond_wrong_type(mocker, tmp_path):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(function_call=None, content="mock reply"))]
    mocker.patch('webchat.call_llm_with_retry', return_value=mock_response)
    with pytest.raises(TypeError):
        webchat.respond(123, [])

def test_chat_wrong_type(mocker):
    mocker.patch('webchat.respond', return_value=('reply', 'map_html', 'logs', 'table'))
    with pytest.raises(TypeError):
        webchat.chat("msg", 123, None)

def test_build_ui_wrong_type():
    with pytest.raises(TypeError):
        webchat.build_ui(123)

def test_main_wrong_type():
    with pytest.raises(TypeError):
        webchat.main(123)
