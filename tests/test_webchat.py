from webchat import infer_location, extract_map_coords, respond, chat, parse_table_coordinates
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

@pytest.mark.parametrize("empty_str", ["", "   "])
def test_infer_location_empty_strings(empty_str):
    assert infer_location(empty_str) is None

@pytest.mark.parametrize("empty_str", ["", "   "])
def test_parse_table_coordinates_empty_strings(empty_str):
    assert parse_table_coordinates(empty_str, 0, 1) == []

@pytest.mark.parametrize("empty_str", ["", "   "])
def test_parse_distance_table_empty_strings(empty_str):
    assert parse_distance_table(empty_str) == []

@pytest.mark.parametrize("empty_str", ["", "   "])
def test_extract_map_coords_empty_strings(empty_str):
    assert extract_map_coords(empty_str, empty_str) == []
    assert extract_map_coords("geocode_locations", empty_str) == []
    assert extract_map_coords(empty_str, "table") == []

@pytest.mark.xfail(reason="Bug: accepts empty/whitespace messages instead of raising ValueError or ignoring")
@pytest.mark.parametrize("empty_str", ["", "   "])
def test_respond_empty_strings(empty_str, mocker, tmp_path):
    mock_llm = mocker.patch("webchat.call_llm_with_retry")
    mock_msg = mocker.MagicMock()
    mock_msg.content = "response"
    mock_msg.function_call = None
    mock_llm.return_value.choices = [mocker.MagicMock(message=mock_msg)]

    class MockFile:
        name = str(tmp_path / "test.txt")

    with open(MockFile.name, "w") as f:
        f.write("test")

    # Current behavior just passes through; xfail asserts it should be caught
    with pytest.raises(ValueError):
        respond(empty_str, [], upload_file=MockFile())

@pytest.mark.xfail(reason="Bug: accepts empty/whitespace messages instead of raising ValueError or ignoring")
@pytest.mark.parametrize("empty_str", ["", "   "])
def test_chat_empty_strings(empty_str, mocker, tmp_path):
    mock_llm = mocker.patch("webchat.call_llm_with_retry")
    mock_msg = mocker.MagicMock()
    mock_msg.content = "response"
    mock_msg.function_call = None
    mock_llm.return_value.choices = [mocker.MagicMock(message=mock_msg)]

    class MockFile:
        name = str(tmp_path / "test.txt")

    with open(MockFile.name, "w") as f:
        f.write("test")

    # Current behavior just passes through; xfail asserts it should be caught
    with pytest.raises(ValueError):
        chat(empty_str, [], upload_file=MockFile())
