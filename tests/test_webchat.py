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

import os
import pytest
from webchat import respond, chat

class MockUploadFile:
    def __init__(self, name):
        self.name = name

@pytest.mark.skipif(os.name == 'nt' or os.geteuid() == 0, reason="Skip on Windows or when root")
@pytest.mark.xfail(reason="Looks like a bug: silently catches exception from unreadable file but continues and fails network call")
def test_respond_unreadable_file(tmp_path, mocker):
    f = tmp_path / "test.txt"
    f.touch()
    f.chmod(0)
    upload_file = MockUploadFile(str(f))

    mocker.patch('webchat.call_llm_with_retry')

    with pytest.raises(PermissionError):
        respond("hello", [], upload_file)

@pytest.mark.skipif(os.name == 'nt' or os.geteuid() == 0, reason="Skip on Windows or when root")
@pytest.mark.xfail(reason="Looks like a bug: chat silently catches exception from unreadable file")
def test_chat_unreadable_file(tmp_path, mocker):
    f = tmp_path / "test.txt"
    f.touch()
    f.chmod(0)
    upload_file = MockUploadFile(str(f))

    mocker.patch('webchat.call_llm_with_retry')

    with pytest.raises(PermissionError):
        chat("hello", [], upload_file)
