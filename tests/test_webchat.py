import os
from types import SimpleNamespace
from webchat import respond
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

@pytest.mark.xfail(reason="looks like a bug when relative paths are used for uploads and directory changes")
def test_respond_relative_path_bug(mocker, tmp_path, monkeypatch):
    class MockFile:
        def __init__(self, name):
            self.name = name

    def mock_llm(*args, **kwargs):
        messages = kwargs.get('messages', [])
        last_msg = messages[-1]['content']
        return SimpleNamespace(choices=[
            SimpleNamespace(message=SimpleNamespace(
                function_call=None,
                content=f"Echo: {last_msg}"
            ))
        ])

    mocker.patch('webchat.call_llm_with_retry', side_effect=mock_llm)

    with open("dummy_upload.txt", "w") as f:
        f.write("dummy content")

    upload = MockFile("dummy_upload.txt")

    res1 = respond("Hello", [], upload)

    monkeypatch.chdir(tmp_path)
    res2 = respond("Hello", [], upload)

    assert res1 == res2
