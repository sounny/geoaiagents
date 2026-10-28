from unittest.mock import MagicMock
import webchat
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

def test_infer_location_twice():
    out1 = webchat.infer_location("show map for Paris")
    out2 = webchat.infer_location("show map for Paris")
    assert out1 == out2

def test_parse_table_coordinates_twice():
    table = "| Lat | Lon |\n|---|---|\n| 48.8 | 2.3 |"
    out1 = webchat.parse_table_coordinates(table, 0, 1)
    out2 = webchat.parse_table_coordinates(table, 0, 1)
    assert out1 == out2

def test_parse_distance_table_twice():
    table = "| Lat1 | Lon1 | Lat2 | Lon2 |\n|---|---|---|---|\n| 48.8 | 2.3 | 51.5 | -0.1 |"
    out1 = webchat.parse_distance_table(table)
    out2 = webchat.parse_distance_table(table)
    assert out1 == out2

def test_extract_map_coords_twice():
    table = "| Location | Address | Lat | Lon |\n|---|---|---|---|\n| Paris | Paris, FR | 48.8 | 2.3 |"
    out1 = webchat.extract_map_coords("geocode_locations", table)
    out2 = webchat.extract_map_coords("geocode_locations", table)
    assert out1 == out2

def test_run_tool_twice(mocker):
    m_invoke = mocker.patch("webchat.registry.invoke", return_value="table")
    call = MagicMock()
    call.name = "tool_name"
    call.arguments = "{}"
    out1 = webchat.run_tool(call)
    out2 = webchat.run_tool(call)
    assert out1 == out2

def test_respond_twice(mocker):
    webchat.LAST_MAP_HTML = ""
    m_llm = mocker.patch("webchat.call_llm_with_retry")
    mocker.patch.object(webchat, "messages", [])
    msg_mock = MagicMock()
    msg_mock.content = "response"
    msg_mock.function_call = None
    choice_mock = MagicMock()
    choice_mock.message = msg_mock
    m_llm.return_value = MagicMock(choices=[choice_mock])

    webchat.log_history.clear()
    out1 = webchat.respond("hello", [])
    webchat.log_history.clear()
    out2 = webchat.respond("hello", [])
    assert out1 == out2

def test_chat_twice(mocker):
    webchat.LAST_MAP_HTML = ""
    m_llm = mocker.patch("webchat.call_llm_with_retry")
    mocker.patch.object(webchat, "messages", [])
    msg_mock = MagicMock()
    msg_mock.content = "response"
    msg_mock.function_call = None
    choice_mock = MagicMock()
    choice_mock.message = msg_mock
    m_llm.return_value = MagicMock(choices=[choice_mock])

    webchat.log_history.clear()
    out1 = webchat.chat("hello", [], None)
    webchat.log_history.clear()
    out2 = webchat.chat("hello", [], None)
    assert out1 == out2

def test_main_twice(mocker):
    m_build_ui = mocker.patch("webchat.build_ui")
    out1 = webchat.main()
    out2 = webchat.main()
    assert out1 == out2

@pytest.mark.xfail(reason="create_map_html generates non-deterministic UUIDs for map ids")
def test_create_map_html_twice():
    out1 = webchat.create_map_html([(48.8, 2.3)])
    out2 = webchat.create_map_html([(48.8, 2.3)])
    assert out1 == out2

@pytest.mark.xfail(raises=TypeError, reason="gradio Chatbot component initialization raises TypeError on unexpectedly typed kwarg")
def test_build_ui_twice(mocker):
    mocker.patch("gradio.Blocks")
    out1 = webchat.build_ui()
    out2 = webchat.build_ui()
    assert out1 == out2
