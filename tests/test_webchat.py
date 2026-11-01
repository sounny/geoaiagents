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

from unittest.mock import MagicMock, patch
import webchat

def test_webchat_string_nul():
    assert webchat.infer_location("for \x00") is None
    assert webchat.extract_map_coords("tool", "table\x00data") == []
    assert webchat.parse_distance_table("table\x00data") == []
    assert webchat.parse_table_coordinates("table\x00data", 1, 2) == []

@pytest.mark.xfail(reason="Swallows ValueError from embedded null byte in file path instead of propagating")
def test_webchat_respond_nul_swallows_exception():
    upload_file = MagicMock()
    upload_file.name = "test\x00.txt"

    with patch("webchat.call_llm_with_retry") as mock_call:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.function_call = None
        mock_response.choices[0].message.content = "mocked"
        mock_call.return_value = mock_response

        with pytest.raises(ValueError):
            webchat.respond("msg\x00", [], upload_file)

@pytest.mark.xfail(reason="Swallows ValueError from embedded null byte in file path instead of propagating")
def test_webchat_chat_nul_swallows_exception():
    upload_file = MagicMock()
    upload_file.name = "test\x00.txt"

    with patch("webchat.call_llm_with_retry") as mock_call:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.function_call = None
        mock_response.choices[0].message.content = "mocked"
        mock_call.return_value = mock_response

        with pytest.raises(ValueError):
            webchat.chat("msg\x00", [], upload_file)
