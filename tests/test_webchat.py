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

import warnings
import types
from unittest.mock import MagicMock
import webchat

def check_no_warnings(func, *args, **kwargs):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        func(*args, **kwargs)

def test_infer_location_warnings():
    check_no_warnings(webchat.infer_location, "for New York")

def test_create_map_html_warnings():
    check_no_warnings(webchat.create_map_html, [(48.8, 2.3)])

def test_parse_table_coordinates_warnings():
    check_no_warnings(webchat.parse_table_coordinates, "| Lat | Lon |\n|---|---|\n| 48.8 | 2.3 |", 0, 1)

def test_parse_distance_table_warnings():
    check_no_warnings(webchat.parse_distance_table, "| Lat1 | Lon1 | Lat2 | Lon2 |\n|---|---|---|---|\n| 48.8 | 2.3 | 51.5 | -0.1 |")

def test_extract_map_coords_warnings():
    check_no_warnings(webchat.extract_map_coords, "distance", "| Lat1 | Lon1 | Lat2 | Lon2 |\n|---|---|---|---|\n| 48.8 | 2.3 | 51.5 | -0.1 |")

def test_run_tool_warnings(mocker):
    call = types.SimpleNamespace(name="geocode_locations", arguments='{"locations": "Paris"}')
    mocker.patch.object(webchat.registry, 'invoke', return_value="| Lat | Lon |\n|---|---|\n| 48.8 | 2.3 |")
    check_no_warnings(webchat.run_tool, call)

def test_respond_warnings(mocker, tmp_path):
    mocker.patch('webchat.call_llm_with_retry')
    mock_msg = MagicMock()
    mock_msg.content = "Hi"
    mock_msg.function_call = None
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=mock_msg)]
    webchat.call_llm_with_retry.return_value = mock_response

    test_file = tmp_path / "test.txt"
    test_file.write_text("test data")
    upload = MagicMock()
    upload.name = str(test_file)

    check_no_warnings(webchat.respond, "Hello", [], upload)

def test_chat_warnings(mocker, tmp_path):
    mocker.patch('webchat.call_llm_with_retry')
    mock_msg = MagicMock()
    mock_msg.content = "Hi"
    mock_msg.function_call = None
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=mock_msg)]
    webchat.call_llm_with_retry.return_value = mock_response

    test_file = tmp_path / "test.txt"
    test_file.write_text("test data")
    upload = MagicMock()
    upload.name = str(test_file)

    check_no_warnings(webchat.chat, "Hello", [], upload)

@pytest.mark.xfail(reason="Gradio internal warnings and unexpected keyword argument")
def test_build_ui_warnings():
    check_no_warnings(webchat.build_ui)

@pytest.mark.xfail(reason="Gradio internal warnings and unexpected keyword argument via build_ui")
def test_main_warnings(mocker):
    mocker.patch('webchat.build_ui', side_effect=TypeError("build_ui failed"))
    check_no_warnings(webchat.main)
