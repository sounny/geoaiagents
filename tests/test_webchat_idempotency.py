import pytest
import os
import sys
import copy
import re
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import webchat

def normalize_html(html_str: str) -> str:
    if isinstance(html_str, str):
        return re.sub(r'[a-f0-9]{32}', 'UUID', html_str)
    return html_str

def test_infer_location_idempotency(mocker):
    # Mocking external calls just in case the implementation changes to use them
    mocker.patch("webchat.call_llm_with_retry")
    mocker.patch("webchat.client")

    msg = "for Paris"
    orig_msg = copy.deepcopy(msg)
    res1 = webchat.infer_location(msg)
    res2 = webchat.infer_location(msg)
    assert res1 == res2
    assert msg == orig_msg

def test_create_map_html_idempotency(mocker):
    mocker.patch("webchat.call_llm_with_retry")
    mocker.patch("webchat.client")

    points = [(48.8, 2.3)]
    orig_points = copy.deepcopy(points)
    res1 = webchat.create_map_html(points)
    res2 = webchat.create_map_html(points)
    assert normalize_html(res1) == normalize_html(res2)
    assert points == orig_points

def test_parse_table_coordinates_idempotency(mocker):
    mocker.patch("webchat.call_llm_with_retry")
    mocker.patch("webchat.client")

    table = "| Lat | Lon |\n|---|---|\n| 1.0 | 2.0 |"
    lat_idx, lon_idx = 0, 1
    orig_table = copy.deepcopy(table)
    res1 = webchat.parse_table_coordinates(table, lat_idx, lon_idx)
    res2 = webchat.parse_table_coordinates(table, lat_idx, lon_idx)
    assert res1 == res2
    assert table == orig_table

def test_parse_distance_table_idempotency(mocker):
    mocker.patch("webchat.call_llm_with_retry")
    mocker.patch("webchat.client")

    table = "| Lat1 | Lon1 | Lat2 | Lon2 |\n|---|---|---|---|\n| 1.0 | 2.0 | 3.0 | 4.0 |"
    orig_table = copy.deepcopy(table)
    res1 = webchat.parse_distance_table(table)
    res2 = webchat.parse_distance_table(table)
    assert res1 == res2
    assert table == orig_table

def test_extract_map_coords_idempotency(mocker):
    mocker.patch("webchat.call_llm_with_retry")
    mocker.patch("webchat.client")

    tool = "distance"
    table = "| Lat1 | Lon1 | Lat2 | Lon2 |\n|---|---|---|---|\n| 1.0 | 2.0 | 3.0 | 4.0 |"
    orig_tool = copy.deepcopy(tool)
    orig_table = copy.deepcopy(table)
    res1 = webchat.extract_map_coords(tool, table)
    res2 = webchat.extract_map_coords(tool, table)
    assert res1 == res2
    assert tool == orig_tool
    assert table == orig_table

def test_run_tool_idempotency(mocker):
    mocker.patch("webchat.call_llm_with_retry")
    mocker.patch("webchat.client")

    mocker.patch.object(webchat.registry, "invoke", return_value="table")
    class DummyCall:
        name = "geocode_locations"
        arguments = "{}"
    call = DummyCall()
    orig_call_name = copy.deepcopy(call.name)
    orig_call_args = copy.deepcopy(call.arguments)
    res1 = webchat.run_tool(call)
    res2 = webchat.run_tool(call)
    assert res1 == res2
    assert call.name == orig_call_name
    assert call.arguments == orig_call_args

def test_respond_idempotency(mocker, tmp_path):
    mock_llm = mocker.patch("webchat.call_llm_with_retry")
    mock_msg = MagicMock()
    mock_msg.function_call = None
    mock_msg.content = "mock response"
    mock_choice = MagicMock()
    mock_choice.message = mock_msg
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_llm.return_value = mock_response

    mocker.patch("webchat.infer_location", return_value=None)
    mocker.patch.object(webchat.registry, "invoke", return_value="")

    mock_file = tmp_path / "test.txt"
    mock_file.write_text("dummy")

    class DummyUpload:
        name = str(mock_file)

    upload = DummyUpload()

    original_messages = copy.deepcopy(webchat.messages)
    original_log_history = copy.deepcopy(webchat.log_history)
    original_last_map = webchat.LAST_MAP_HTML

    msg = "hello"
    history = []

    orig_msg = copy.deepcopy(msg)
    orig_history = copy.deepcopy(history)
    orig_upload_name = copy.deepcopy(upload.name)

    try:
        res1 = webchat.respond(msg, history, upload)

        # Reset state for identical results
        webchat.messages.clear()
        webchat.messages.extend(copy.deepcopy(original_messages))
        webchat.log_history.clear()
        webchat.log_history.extend(copy.deepcopy(original_log_history))
        webchat.LAST_MAP_HTML = original_last_map

        res2 = webchat.respond(msg, history, upload)

        assert res1[0] == res2[0]
        assert normalize_html(res1[1]) == normalize_html(res2[1])
        assert res1[2] == res2[2]
        assert res1[3] == res2[3]

        assert msg == orig_msg
        assert history == orig_history
        assert upload.name == orig_upload_name
    finally:
        webchat.messages.clear()
        webchat.messages.extend(original_messages)
        webchat.log_history.clear()
        webchat.log_history.extend(original_log_history)
        webchat.LAST_MAP_HTML = original_last_map

def test_chat_idempotency(mocker, tmp_path):
    mocker.patch("webchat.call_llm_with_retry")
    mocker.patch("webchat.client")

    mocker.patch("webchat.respond", return_value=("reply", "map_html", "logs", "table"))

    mock_file = tmp_path / "test.txt"
    mock_file.write_text("dummy")
    class DummyUpload:
        name = str(mock_file)
    upload = DummyUpload()

    msg = "msg"
    history = []

    orig_msg = copy.deepcopy(msg)
    orig_history = copy.deepcopy(history)
    orig_upload_name = copy.deepcopy(upload.name)

    res1 = webchat.chat(msg, history, upload)
    res2 = webchat.chat(msg, history, upload)

    assert res1 == res2
    assert msg == orig_msg
    assert history == orig_history
    assert upload.name == orig_upload_name

def test_build_ui_idempotency(mocker):
    mocker.patch("webchat.call_llm_with_retry")
    mocker.patch("webchat.client")

    mock_gr = mocker.patch("webchat.gr")
    mock_demo = MagicMock()
    # Force Blocks to return identical object across calls
    mock_gr.Blocks.return_value = mock_demo
    mock_gr.Blocks.return_value.__enter__.return_value = mock_demo

    res1 = webchat.build_ui()
    res2 = webchat.build_ui()
    assert res1 == res2

def test_main_idempotency(mocker):
    mocker.patch("webchat.call_llm_with_retry")
    mocker.patch("webchat.client")

    mock_build = mocker.patch("webchat.build_ui")
    mock_demo = MagicMock()
    mock_build.return_value = mock_demo

    res1 = webchat.main()
    res2 = webchat.main()

    assert res1 == res2
