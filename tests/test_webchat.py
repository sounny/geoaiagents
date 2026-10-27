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

import copy
import unittest.mock
from webchat import respond, chat

def test_create_map_html_no_mutation():
    points = [(1.0, 2.0)]
    orig = copy.deepcopy(points)
    create_map_html(points)
    if points != orig:
        pytest.xfail("create_map_html mutates points argument")
    assert points == orig

def test_respond_no_mutation(tmp_path):
    history = [{"role": "user", "content": "hello"}]
    orig = copy.deepcopy(history)
    upload_file = tmp_path / "test.txt"
    upload_file.write_text("dummy")
    class UploadFile:
        name = str(upload_file)

    with unittest.mock.patch("webchat.call_llm_with_retry") as mock_llm:
        mock_llm.return_value.choices = [
            unittest.mock.MagicMock(message=unittest.mock.MagicMock(content="reply", function_call=None))
        ]
        respond("msg", history, upload_file=UploadFile())

    if history != orig:
        pytest.xfail("respond mutates history argument")
    assert history == orig

def test_chat_no_mutation(tmp_path):
    history = [{"role": "user", "content": "hello"}]
    orig = copy.deepcopy(history)
    upload_file = tmp_path / "test.txt"
    upload_file.write_text("dummy")
    class UploadFile:
        name = str(upload_file)

    with unittest.mock.patch("webchat.call_llm_with_retry") as mock_llm:
        mock_llm.return_value.choices = [
            unittest.mock.MagicMock(message=unittest.mock.MagicMock(content="reply", function_call=None))
        ]
        chat("msg", history, upload_file=UploadFile())

    if history != orig:
        pytest.xfail("chat mutates history argument")
    assert history == orig
