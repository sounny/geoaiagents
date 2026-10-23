import pytest
from webchat import parse_distance_table

def test_parse_distance_table_locking_header_only_empty():
    assert parse_distance_table('| A | B | C | D |\n|---|---|---|---|') == []

    table = '| Lat1 | Lon1 | Lat2 | Lon2 |\n|---|---|---|---|\n| 48.8 | 2.3 | 51.5 | -0.1 |'
    assert parse_distance_table(table) == [(48.8, 2.3), (51.5, -0.1)]

from webchat import (
    parse_table_coordinates,
    create_map_html,
    infer_location,
    extract_map_coords,
    respond,
    chat
)
import re
from types import SimpleNamespace

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

TEXT_INPUTS = [
    "",
    "   ",
    "\t\n \t",
    "\n\t padding \n\t"
]

@pytest.mark.parametrize("text", TEXT_INPUTS)
def test_infer_location_edge_cases(text):
    assert infer_location(text) is None

@pytest.mark.parametrize("text", TEXT_INPUTS)
def test_parse_table_coordinates_edge_cases(text):
    assert parse_table_coordinates(text, 0, 1) == []

@pytest.mark.parametrize("text", TEXT_INPUTS)
def test_parse_distance_table_edge_cases(text):
    assert parse_distance_table(text) == []

@pytest.mark.parametrize("text", TEXT_INPUTS)
def test_extract_map_coords_edge_cases(text):
    assert extract_map_coords("distance", text) == []
    assert extract_map_coords(text, "valid_table_placeholder") == []

@pytest.mark.parametrize("text", TEXT_INPUTS)
def test_respond_edge_cases(mocker, text):
    mock_llm = mocker.patch('webchat.call_llm_with_retry')
    mock_message = SimpleNamespace(content="mocked reply", function_call=None)
    mock_choice = SimpleNamespace(message=mock_message)
    mock_response = SimpleNamespace(choices=[mock_choice])
    mock_llm.return_value = mock_response

    reply, map_html, logs, table = respond(text, [], None)
    assert reply == "mocked reply"

@pytest.mark.parametrize("text", TEXT_INPUTS)
def test_chat_edge_cases(mocker, text):
    mock_llm = mocker.patch('webchat.call_llm_with_retry')
    mock_message = SimpleNamespace(content="mocked reply", function_call=None)
    mock_choice = SimpleNamespace(message=mock_message)
    mock_response = SimpleNamespace(choices=[mock_choice])
    mock_llm.return_value = mock_response

    history, map_html, logs, table = chat(text, [], None)
    assert history == [
        {"role": "user", "content": text},
        {"role": "assistant", "content": "mocked reply"}
    ]
