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
import copy
import inspect
import webchat
import os

@pytest.mark.parametrize("func_name", [
    "build_ui",
    "chat",
    "create_map_html",
    "extract_map_coords",
    "infer_location",
    "main",
    "parse_distance_table",
    "parse_table_coordinates",
    "respond",
    "run_tool"
])
def test_public_functions_purity_locking(func_name, mocker, tmp_path):
    mock_msg = MagicMock()
    mock_msg.choices = [MagicMock()]
    mock_msg.choices[0].message.content = "mocked response"
    mock_msg.choices[0].message.function_call = None
    mocker.patch("webchat.call_llm_with_retry", return_value=mock_msg)

    mock_func_call = MagicMock()
    mock_func_call.name = "geocode_locations"
    mock_func_call.arguments = '{"locations": "Paris"}'

    table_str = "| A | B | C | D |\n|---|---|---|---|\n| 1 | 2 | 3 | 4 |"

    # Use tmp_path for filesystem mock
    upload = MagicMock()
    upload.name = str(tmp_path / "test.txt")
    with open(upload.name, "w") as f:
        f.write("test content")

    args_map = {
        "build_ui": ([], {}),
        "chat": (["msg", [], upload], {}),
        "create_map_html": ([[(0.0, 0.0)]], {}),
        "extract_map_coords": (["distance", table_str], {}),
        "infer_location": (["map for Paris"], {}),
        "main": ([], {}),
        "parse_distance_table": ([table_str], {}),
        "parse_table_coordinates": ([table_str, 0, 1], {}),
        "respond": (["msg", [], upload], {}),
        "run_tool": ([mock_func_call], {})
    }

    if func_name in ["chat", "respond", "run_tool"]:
        pytest.xfail(f"{func_name} relies on global state (messages, log_history) and is not pure")

    if func_name == "build_ui":
        pytest.xfail("build_ui cannot be cleanly tested for purity due to gradio Blocks context and side effects")

    if func_name == "main":
        mocker.patch("webchat.build_ui")

    func = getattr(webchat, func_name)
    args, kwargs = args_map[func_name]

    r1 = func(*copy.deepcopy(args), **copy.deepcopy(kwargs))

    if isinstance(r1, MagicMock) or r1 is None:
        r1_orig = r1
    else:
        r1_orig = copy.deepcopy(r1)

    if isinstance(r1, list):
        r1.append("mutated")
    elif isinstance(r1, dict):
        r1["mutated"] = "mutated"
    elif isinstance(r1, tuple):
        for item in r1:
            if isinstance(item, list):
                item.append("mutated")
            elif isinstance(item, dict):
                item["mutated"] = "mutated"

    r2 = func(*copy.deepcopy(args), **copy.deepcopy(kwargs))

    if func_name == "create_map_html":
        # Folium generates random IDs in HTML
        r1_orig = re.sub(r'[0-9a-f]{32}', 'UUID', r1_orig)
        r2 = re.sub(r'[0-9a-f]{32}', 'UUID', r2)

    if not isinstance(r1, MagicMock):
        assert r2 == r1_orig, f"{func_name} failed purity test"
