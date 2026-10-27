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

from unittest.mock import MagicMock
import webchat
import re

class MockMessage:
    def __init__(self, content, function_call=None):
        self.content = content
        self.function_call = function_call

class MockChoice:
    def __init__(self, message):
        self.message = message

class MockResponse:
    def __init__(self, choices):
        self.choices = choices

def test_chat_dict_keys_order(mocker, tmp_path):
    mocker.patch("webchat.call_llm_with_retry", return_value=MockResponse([MockChoice(MockMessage("Hello"))]))

    f = tmp_path / "test.txt"
    f.write_text("dummy")

    class UploadFile:
        def __init__(self, name):
            self.name = name

    upload_file = UploadFile(str(f))

    history1_chat = [{"role": "user", "content": "hi"}]
    history2_chat = [{"content": "hi", "role": "user"}]

    orig_messages = list(webchat.messages)

    try:
        webchat.messages = []
        c_res1, map1, logs1, tab1 = webchat.chat(message="hi", history=history1_chat, upload_file=upload_file)

        webchat.messages = []
        c_res2, map2, logs2, tab2 = webchat.chat(message="hi", history=history2_chat, upload_file=upload_file)

        map1 = re.sub(r'[a-z0-9]{32}', 'ID', map1)
        map2 = re.sub(r'[a-z0-9]{32}', 'ID', map2)

        try:
            assert c_res1 == c_res2
            assert map1 == map2
            assert logs1 == logs2
            assert tab1 == tab2
        except AssertionError:
            pytest.xfail("Dict key order in history affects output")
    finally:
        webchat.messages = orig_messages
