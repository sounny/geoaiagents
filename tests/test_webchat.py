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
from unittest.mock import patch, MagicMock

class DummyUpload:
    def __init__(self, name):
        self.name = name

@pytest.mark.xfail(reason="looks like a bug where directories are silently ignored instead of throwing IsADirectoryError")
def test_respond_directory_error_xfail(tmp_path):
    from webchat import respond
    upload = DummyUpload(str(tmp_path))
    with patch('webchat.call_llm_with_retry') as mock_call:
        mock_msg = MagicMock()
        mock_msg.content = "mock response"
        mock_msg.function_call = None
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=mock_msg)]
        mock_call.return_value = mock_response
        with pytest.raises(IsADirectoryError):
            respond("hello", [], upload)

@pytest.mark.xfail(reason="looks like a bug where directories are silently ignored instead of throwing IsADirectoryError")
def test_chat_directory_error_xfail(tmp_path):
    from webchat import chat
    upload = DummyUpload(str(tmp_path))
    with patch('webchat.call_llm_with_retry') as mock_call:
        mock_msg = MagicMock()
        mock_msg.content = "mock response"
        mock_msg.function_call = None
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=mock_msg)]
        mock_call.return_value = mock_response
        with pytest.raises(IsADirectoryError):
            chat("hello", [], upload)
