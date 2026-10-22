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

from unittest.mock import patch
import logging
from webchat import respond

@patch("webchat.call_llm_with_retry")
def test_webchat_logging_normal(mock_call_llm, caplog):
    caplog.set_level(logging.DEBUG)

    # Mocking a normal response
    class MockMessage:
        content = "Hello there!"
        function_call = None

    class MockChoice:
        message = MockMessage()

    class MockResponse:
        choices = [MockChoice()]

    mock_call_llm.return_value = MockResponse()

    # Call the respond function
    respond("Show me a map of Berlin", [])

    # Check logs for DEBUG and INFO
    log_levels = [record.levelname for record in caplog.records]
    assert "DEBUG" in log_levels, "Expected DEBUG logs"
    assert "INFO" in log_levels, "Expected INFO logs"

    # Check no secrets in logs
    log_text = caplog.text.lower()
    assert "api_key" not in log_text
    assert "secret" not in log_text
    assert "password" not in log_text

@patch("webchat.call_llm_with_retry")
def test_webchat_logging_failing(mock_call_llm, caplog):
    caplog.set_level(logging.DEBUG)

    # Mocking a failing response (e.g., API Error)
    mock_call_llm.side_effect = Exception("API connection error")

    # Call the respond function and catch the exception
    try:
        respond("Show me a map of Berlin", [])
    except Exception:
        pass

    # We expect some DEBUG log before the call to llm fails (e.g., Sending to LLM:)
    log_levels = [record.levelname for record in caplog.records]
    assert "DEBUG" in log_levels, "Expected DEBUG logs"

    # Check no secrets in logs
    log_text = caplog.text.lower()
    assert "api_key" not in log_text
    assert "secret" not in log_text
    assert "password" not in log_text
