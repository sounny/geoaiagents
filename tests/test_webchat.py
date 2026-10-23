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

import logging
from unittest.mock import MagicMock
import webchat

def test_run_tool_logging(caplog, mocker):
    caplog.set_level(logging.INFO)
    mocker.patch.object(webchat.registry, 'invoke', return_value="table")
    function_call = MagicMock()
    function_call.name = "test_tool"
    function_call.arguments = "{}"
    webchat.run_tool(function_call)

    assert any(r.levelname == 'INFO' and r.name == 'root' and \
               'Invoking test_tool...' in r.message for r in caplog.records)

def test_respond_normal_no_function_call(caplog, mocker):
    caplog.set_level(logging.DEBUG)
    mock_llm = mocker.patch('webchat.call_llm_with_retry')
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.function_call = None
    mock_response.choices[0].message.content = "hello"
    mock_llm.return_value = mock_response

    mocker.patch('webchat.messages', [{"role": "system", "content": "..."}])

    webchat.respond("hello", [])

    assert any(r.levelname == 'DEBUG' and r.name == 'root' and \
               'Sending to LLM:' in r.message for r in caplog.records)
    assert any(r.levelname == 'DEBUG' and r.name == 'root' and \
               'LLM response:' in r.message for r in caplog.records)
    assert any(r.levelname == 'INFO' and r.name == 'root' and \
               'LLM response received' in r.message for r in caplog.records)

def test_respond_function_call(caplog, mocker):
    caplog.set_level(logging.DEBUG)
    mock_llm = mocker.patch('webchat.call_llm_with_retry')

    mock_resp1 = MagicMock()
    mock_resp1.choices = [MagicMock()]
    mock_resp1.choices[0].message.function_call.name = "some_tool"
    mock_resp1.choices[0].message.function_call.arguments = "{}"

    mock_resp2 = MagicMock()
    mock_resp2.choices = [MagicMock()]
    mock_resp2.choices[0].message.function_call = None
    mock_resp2.choices[0].message.content = "done"

    mock_llm.side_effect = [mock_resp1, mock_resp2]

    mocker.patch('webchat.run_tool', return_value=("some_tool", "table"))
    mocker.patch('webchat.extract_map_coords', return_value=[(0.0, 0.0)])

    mocker.patch('webchat.messages', [{"role": "system", "content": "..."}])

    webchat.respond("do something", [])

    assert any(r.levelname == 'DEBUG' and r.name == 'root' and \
               'Sending to LLM:' in r.message for r in caplog.records)
    assert any(r.levelname == 'DEBUG' and r.name == 'root' and \
               'LLM response:' in r.message for r in caplog.records)
    assert any(r.levelname == 'INFO' and r.name == 'root' and \
               'LLM response received' in r.message for r in caplog.records)

def test_respond_auto_geocoding(caplog, mocker):
    caplog.set_level(logging.DEBUG)
    mock_llm = mocker.patch('webchat.call_llm_with_retry')

    mock_resp1 = MagicMock()
    mock_resp1.choices = [MagicMock()]
    mock_resp1.choices[0].message.function_call = None
    mock_resp1.choices[0].message.content = "I found it"

    mock_resp2 = MagicMock()
    mock_resp2.choices = [MagicMock()]
    mock_resp2.choices[0].message.function_call = None
    mock_resp2.choices[0].message.content = "map updated"

    mock_llm.side_effect = [mock_resp1, mock_resp2]

    mocker.patch('webchat.infer_location', return_value="Paris")
    mocker.patch.object(webchat.registry, 'invoke', return_value="table")
    mocker.patch('webchat.parse_table_coordinates', return_value=[(48.8, 2.3)])

    mocker.patch('webchat.messages', [{"role": "system", "content": "..."}])

    webchat.respond("map for Paris", [])

    assert any(r.levelname == 'INFO' and r.name == 'root' and \
               'Auto geocoding: Paris' in r.message for r in caplog.records)

def test_respond_upload_error(caplog, mocker):
    caplog.set_level(logging.DEBUG)
    mock_llm = mocker.patch('webchat.call_llm_with_retry')
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.function_call = None
    mock_response.choices[0].message.content = "hello"
    mock_llm.return_value = mock_response

    mock_upload = MagicMock()
    mock_upload.name = "nonexistent.txt"

    mocker.patch('webchat.messages', [{"role": "system", "content": "..."}])

    webchat.respond("hello", [], upload_file=mock_upload)

    assert any(r.levelname == 'DEBUG' and r.name == 'root' and \
               'Sending to LLM:' in r.message for r in caplog.records)
