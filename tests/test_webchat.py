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
from types import SimpleNamespace
from webchat import run_tool, respond

def test_run_tool_logging_normal(caplog, mocker):
    mocker.patch("webchat.registry.invoke", return_value="some table")
    func_call = SimpleNamespace(name="my_tool", arguments="{}")
    with caplog.at_level(logging.INFO):
        run_tool(func_call)

    assert "Invoking my_tool..." in caplog.text
    assert any(record.levelno == logging.INFO for record in caplog.records)

@pytest.mark.xfail(reason="Bug: No error logging on invalid tool args", raises=AssertionError)
def test_run_tool_logging_error(caplog):
    func_call = SimpleNamespace(name="my_tool", arguments="invalid json")
    with caplog.at_level(logging.ERROR):
        try:
            run_tool(func_call)
        except Exception:
            pass
    assert any(record.levelno >= logging.ERROR for record in caplog.records)

def test_respond_logging_normal(caplog, mocker):
    mock_msg = SimpleNamespace(function_call=None, content="Reply from LLM")
    mock_choice = SimpleNamespace(message=mock_msg)
    mock_response = SimpleNamespace(choices=[mock_choice])

    mocker.patch("webchat.call_llm_with_retry", return_value=mock_response)
    mocker.patch("webchat.messages", [{"role": "system", "content": "..."}])

    with caplog.at_level(logging.DEBUG):
        respond("hello", [])

    assert "Sending to LLM:" in caplog.text
    assert "LLM response:" in caplog.text
    assert "LLM response received" in caplog.text

    assert any(record.levelno == logging.DEBUG for record in caplog.records)
    assert any(record.levelno == logging.INFO for record in caplog.records)

def test_respond_logging_auto_geocoding(caplog, mocker):
    mock_msg = SimpleNamespace(function_call=None, content="Here is a map")
    mock_choice = SimpleNamespace(message=mock_msg)
    mock_response = SimpleNamespace(choices=[mock_choice])

    mocker.patch("webchat.call_llm_with_retry", return_value=mock_response)
    mocker.patch("webchat.messages", [{"role": "system", "content": "..."}])
    mocker.patch("webchat.registry.invoke", return_value="")

    with caplog.at_level(logging.DEBUG):
        respond("map for London", [])

    assert "Auto geocoding: London" in caplog.text
    assert any(record.levelno == logging.INFO for record in caplog.records)

def test_respond_logging_function_call(caplog, mocker):
    func_call = SimpleNamespace(name="my_tool", arguments="{}")
    mock_msg_func = SimpleNamespace(function_call=func_call, content=None)
    mock_choice_func = SimpleNamespace(message=mock_msg_func)
    mock_response_func = SimpleNamespace(choices=[mock_choice_func])

    mock_msg_reply = SimpleNamespace(function_call=None, content="Reply after function")
    mock_choice_reply = SimpleNamespace(message=mock_msg_reply)
    mock_response_reply = SimpleNamespace(choices=[mock_choice_reply])

    mocker.patch("webchat.call_llm_with_retry", side_effect=[mock_response_func, mock_response_reply])
    mocker.patch("webchat.messages", [{"role": "system", "content": "..."}])
    mocker.patch("webchat.run_tool", return_value=("my_tool", "table"))

    with caplog.at_level(logging.DEBUG):
        respond("hello", [])

    assert "Sending to LLM:" in caplog.text
    assert "LLM response received" in caplog.text

@pytest.mark.xfail(reason="Bug: Exceptions during file upload are swallowed without logging", raises=AssertionError)
def test_respond_logging_error_swallowed(caplog, mocker, tmp_path):
    mock_msg = SimpleNamespace(function_call=None, content="Reply")
    mock_choice = SimpleNamespace(message=mock_msg)
    mock_response = SimpleNamespace(choices=[mock_choice])
    mocker.patch("webchat.call_llm_with_retry", return_value=mock_response)
    mocker.patch("webchat.messages", [{"role": "system", "content": "..."}])

    upload_file = SimpleNamespace(name=str(tmp_path / "does_not_exist.txt"))
    with caplog.at_level(logging.WARNING):
        respond("hello", [], upload_file=upload_file)

    assert any(record.levelno >= logging.WARNING for record in caplog.records)

@pytest.mark.xfail(reason="Bug: LLM exceptions bubble up without logging", raises=AssertionError)
def test_respond_logging_error_bubbles(caplog, mocker):
    mocker.patch("webchat.call_llm_with_retry", side_effect=Exception("API Error"))
    mocker.patch("webchat.messages", [{"role": "system", "content": "..."}])

    with caplog.at_level(logging.ERROR):
        try:
            respond("hello", [])
        except Exception:
            pass

    assert any(record.levelno >= logging.ERROR for record in caplog.records)
