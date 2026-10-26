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
import unittest.mock as mock

def strip_ids(html):
    html = re.sub(r'[a-z0-9]{32}', 'ID', html)
    html = re.sub(r'map_[a-z0-9]+', 'map_ID', html)
    return html

def test_create_map_html_sequence():
    pts_list = [(1.0, 1.0)]
    pts_tuple = ((1.0, 1.0),)
    assert strip_ids(create_map_html(pts_list)) == strip_ids(create_map_html(pts_tuple))

def test_respond_sequence():
    import webchat
    with mock.patch('webchat.call_llm_with_retry') as mock_llm:
        mock_msg = mock.Mock()
        mock_msg.function_call = None
        mock_msg.content = "hi"
        mock_choice = mock.Mock()
        mock_choice.message = mock_msg
        mock_llm.return_value.choices = [mock_choice]

        h_list = [{"role": "user", "content": "hi"}]
        h_tuple = ({"role": "user", "content": "hi"},)

        with mock.patch('webchat.messages', []):
            res_list = webchat.respond("msg", h_list)
        with mock.patch('webchat.messages', []):
            res_tuple = webchat.respond("msg", h_tuple)

        assert res_list == res_tuple

@pytest.mark.xfail(raises=TypeError, reason="chat function concatenates history with a list, which fails for tuples")
def test_chat_sequence():
    import webchat
    with mock.patch('webchat.respond') as mock_respond:
        mock_respond.return_value = ("reply", "html", "logs", "table")
        h_list = [{"role": "user", "content": "hi"}]
        h_tuple = ({"role": "user", "content": "hi"},)

        res_list = webchat.chat("msg", h_list, None)
        res_tuple = webchat.chat("msg", h_tuple, None)
        assert res_list == res_tuple
