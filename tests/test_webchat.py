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
from unittest.mock import patch, MagicMock
from webchat import create_map_html, chat, respond, messages

@pytest.mark.xfail(raises=TypeError, strict=True, reason="create_map_html does not support generators due to indexing")
def test_create_map_html_generator():
    pts = [(48.8, 2.3), (51.5, -0.1)]
    create_map_html((p for p in pts))

def test_create_map_html_list():
    pts = [(48.8, 2.3), (51.5, -0.1)]
    html_list = create_map_html(pts)
    assert "L.map" in html_list

@patch('webchat.respond')
@pytest.mark.xfail(raises=TypeError, strict=True, reason="chat function attempts to concatenate generator with list")
def test_chat_generator(mock_respond):
    mock_respond.return_value = ("reply", "map", "logs", "table")
    history = [{"role": "user", "content": "hi"}]
    chat("hello", (x for x in history), None)

@patch('webchat.respond')
def test_chat_list(mock_respond):
    mock_respond.return_value = ("reply", "map", "logs", "table")
    history = [{"role": "user", "content": "hi"}]
    result_list = chat("hello", history, None)
    assert result_list[0] == history + [{"role": "user", "content": "hello"}, {"role": "assistant", "content": "reply"}]

@patch('webchat.call_llm_with_retry')
def test_respond_list_vs_generator(mock_call):
    mock_msg = MagicMock()
    mock_msg.function_call = None
    mock_msg.content = "hello"
    mock_choice = MagicMock()
    mock_choice.message = mock_msg
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_call.return_value = mock_response

    history = [{"role": "user", "content": "hi"}]

    result_list = respond("hello", history, None)
    assert result_list[0] == "hello"

    result_gen = respond("hello", (x for x in history), None)
    assert result_gen[0] == "hello"
    assert result_list == result_gen
