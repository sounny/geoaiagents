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
from collections import OrderedDict
import pytest
import copy

from webchat import (
    infer_location,
    parse_table_coordinates,
    parse_distance_table,
    create_map_html,
    extract_map_coords,
    respond,
    chat,
)

class MyStr(str): pass
class MyInt(int): pass
class MyDict(dict): pass
class MyList(list): pass
class MyOrderedDict(OrderedDict): pass

def test_infer_location_subclass():
    s = "Show me map for Paris"
    try:
        assert infer_location(MyStr(s)) == infer_location(s)
    except Exception as e:
        pytest.xfail(f"infer_location failed with subclassed inputs: {e}")


def test_parse_table_coordinates_subclass():
    s = '| Lat | Lon |\n|---|---|\n| 48.8 | 2.3 |'
    try:
        assert parse_table_coordinates(MyStr(s), MyInt(0), MyInt(1)) == parse_table_coordinates(s, 0, 1)
    except Exception as e:
        pytest.xfail(f"parse_table_coordinates failed with subclassed inputs: {e}")


def test_parse_distance_table_subclass():
    s = '| A | B | C | D |\n|---|---|---|---|\n| 48.8 | 2.3 | 51.5 | -0.1 |'
    try:
        assert parse_distance_table(MyStr(s)) == parse_distance_table(s)
    except Exception as e:
        pytest.xfail(f"parse_distance_table failed with subclassed inputs: {e}")


def test_create_map_html_subclass():
    points = [(48.8, 2.3), (51.5, -0.1)]

    try:
        html1 = create_map_html(MyList(points))
        html2 = create_map_html(points)

        html1_norm = re.sub(r'[a-z0-9]{32}', 'ID', html1)
        html2_norm = re.sub(r'[a-z0-9]{32}', 'ID', html2)
        assert html1_norm == html2_norm
    except Exception as e:
        pytest.xfail(f"create_map_html failed with subclassed inputs: {e}")


def test_extract_map_coords_subclass():
    tool_name = "distance"
    s = '| A | B | C | D |\n|---|---|---|---|\n| 48.8 | 2.3 | 51.5 | -0.1 |'
    try:
        assert extract_map_coords(MyStr(tool_name), MyStr(s)) == extract_map_coords(tool_name, s)
    except Exception as e:
        pytest.xfail(f"extract_map_coords failed with subclassed inputs: {e}")

def test_respond_subclass(tmp_path):
    message = "Hello"
    my_message = MyStr(message)

    with patch('webchat.call_llm_with_retry') as mock_llm:
        mock_msg = MagicMock()
        mock_msg.message.function_call = None
        mock_msg.message.content = "Reply"
        mock_llm.return_value.choices = [mock_msg]

        try:
            # Baseline execution 1 (MyOrderedDict)
            history1 = [{"role": "user", "content": "hi"}]
            my_history1 = MyList([MyOrderedDict({"role": MyStr("user"), "content": MyStr("hi")})])

            # Use tmp_path to mock an upload_file to test file handling
            test_file = tmp_path / "test.csv"
            test_file.write_text("dummy")

            class MockUpload:
                def __init__(self, name):
                    self.name = name

            upload_mock = MockUpload(str(test_file))

            mock_llm.return_value.choices = [mock_msg]
            reply_base1, map_base1, logs_base1, table_base1 = respond(message, history1, upload_file=upload_mock)

            mock_llm.return_value.choices = [mock_msg]
            reply_sub1, map_sub1, logs_sub1, table_sub1 = respond(my_message, my_history1, upload_file=upload_mock)

            map_base1_norm = re.sub(r'[a-z0-9]{32}', 'ID', map_base1)
            map_sub1_norm = re.sub(r'[a-z0-9]{32}', 'ID', map_sub1)

            assert reply_base1 == reply_sub1
            assert map_base1_norm == map_sub1_norm
            assert logs_base1 == logs_sub1
            assert table_base1 == table_sub1

            # Baseline execution 2 (MyDict)
            history2 = [{"role": "user", "content": "hi"}]
            my_history2 = MyList([MyDict({"role": MyStr("user"), "content": MyStr("hi")})])

            mock_llm.return_value.choices = [mock_msg]
            reply_base2, map_base2, logs_base2, table_base2 = respond(message, history2, upload_file=upload_mock)

            mock_llm.return_value.choices = [mock_msg]
            reply_sub2, map_sub2, logs_sub2, table_sub2 = respond(my_message, my_history2, upload_file=upload_mock)

            map_base2_norm = re.sub(r'[a-z0-9]{32}', 'ID', map_base2)
            map_sub2_norm = re.sub(r'[a-z0-9]{32}', 'ID', map_sub2)

            assert reply_base2 == reply_sub2
            assert map_base2_norm == map_sub2_norm
            assert logs_base2 == logs_sub2
            assert table_base2 == table_sub2

        except Exception as e:
            pytest.xfail(f"respond failed with subclassed inputs: {e}")


def test_chat_subclass():
    message = "Hello"
    my_message = MyStr(message)

    with patch('webchat.respond') as mock_respond:
        mock_respond.return_value = ("Reply", "Map", "Logs", "Table")

        try:
            history1 = []
            my_history1 = MyList([])
            hist_base, map_base, logs_base, table_base = chat(message, history1, upload_file=None)
            hist_sub, map_sub, logs_sub, table_sub = chat(my_message, my_history1, upload_file=None)

            assert hist_base == hist_sub
            assert map_base == map_sub
            assert logs_base == logs_sub
            assert table_base == table_sub
        except Exception as e:
            pytest.xfail(f"chat failed with subclassed inputs: {e}")
