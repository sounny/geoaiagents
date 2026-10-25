import pytest
from unittest.mock import MagicMock, ANY
import webchat
import re
import copy
import gradio as gr

def test_infer_location():
    msg = "map for New York"
    pos = webchat.infer_location(msg)
    kw = webchat.infer_location(message=msg)
    assert pos == kw == "New York"

def test_create_map_html():
    pts = [(1.0, 2.0)]
    pos = webchat.create_map_html(pts)
    kw = webchat.create_map_html(points=pts)
    def normalize_html(html):
        # normalize any hash-like string in the html to just hash_id
        return re.sub(r'[a-f0-9]{32}', 'hash_id', html)
    assert normalize_html(pos) == normalize_html(kw)

def test_parse_table_coordinates():
    table = "| Lat | Lon |\n|---|---|\n| 1.0 | 2.0 |"
    pos = webchat.parse_table_coordinates(table, 0, 1)
    kw = webchat.parse_table_coordinates(table=table, lat_index=0, lon_index=1)
    assert pos == kw == [(1.0, 2.0)]

def test_parse_distance_table():
    table = "| Lat1 | Lon1 | Lat2 | Lon2 |\n|---|---|---|---|\n| 1.0 | 2.0 | 3.0 | 4.0 |"
    pos = webchat.parse_distance_table(table)
    kw = webchat.parse_distance_table(table=table)
    assert pos == kw == [(1.0, 2.0), (3.0, 4.0)]

def test_extract_map_coords(mocker):
    # extract_map_coords checks tool_name in DEFAULT_TOOL_COORD_PARSERS
    mocker.patch.dict('webchat.DEFAULT_TOOL_COORD_PARSERS', {"distance": "distance"})
    table = "| Lat1 | Lon1 | Lat2 | Lon2 |\n|---|---|---|---|\n| 1.0 | 2.0 | 3.0 | 4.0 |"
    pos = webchat.extract_map_coords("distance", table)
    kw = webchat.extract_map_coords(tool_name="distance", table=table)
    assert pos == kw == [(1.0, 2.0), (3.0, 4.0)]

def test_run_tool(mocker):
    mocker.patch('webchat.registry.invoke', return_value="table")
    mocker.patch('webchat.parse_tool_args', return_value={})
    function_call = MagicMock()
    function_call.arguments = "{}"
    function_call.name = "tool"
    pos = webchat.run_tool(function_call)
    kw = webchat.run_tool(function_call=function_call)
    assert pos == kw == ("tool", "table")

def test_respond(mocker, tmp_path):
    mock_llm = mocker.patch('webchat.call_llm_with_retry')
    mock_llm_response = MagicMock()
    mock_llm_response.choices[0].message.content = "hello"
    mock_llm_response.choices[0].message.function_call = None
    mock_llm.return_value = mock_llm_response

    mocker.patch('webchat.registry.invoke', return_value="table")

    upload_file = MagicMock()
    file_path = tmp_path / "test.txt"
    file_path.write_text("hello world")
    upload_file.name = str(file_path)

    pos = webchat.respond("msg", [], upload_file)
    webchat.messages = [{"role": "system", "content": webchat.system_prompt}]

    kw = webchat.respond(message="msg", history=[], upload_file=upload_file)
    webchat.messages = [{"role": "system", "content": webchat.system_prompt}]

    assert pos == kw

def test_chat(mocker, tmp_path):
    mock_llm = mocker.patch('webchat.call_llm_with_retry')
    mock_llm_response = MagicMock()
    mock_llm_response.choices[0].message.content = "hello"
    mock_llm_response.choices[0].message.function_call = None
    mock_llm.return_value = mock_llm_response

    mocker.patch('webchat.registry.invoke', return_value="table")

    upload_file = MagicMock()
    file_path = tmp_path / "test.txt"
    file_path.write_text("hello world")
    upload_file.name = str(file_path)

    pos = webchat.chat("msg", [], upload_file)
    webchat.messages = [{"role": "system", "content": webchat.system_prompt}]

    kw = webchat.chat(message="msg", history=[], upload_file=upload_file)
    webchat.messages = [{"role": "system", "content": webchat.system_prompt}]

    assert pos == kw

def test_build_ui(mocker):
    mocker.patch('gradio.Chatbot')
    pos = webchat.build_ui()
    assert isinstance(pos, gr.Blocks)

def test_main(mocker):
    mock_build_ui = mocker.patch('webchat.build_ui')
    mock_demo = MagicMock()
    mock_build_ui.return_value = mock_demo
    webchat.main()
    mock_demo.launch.assert_called_once()
