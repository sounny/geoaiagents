import pytest

import re
from unittest.mock import MagicMock
from webchat import (
    parse_distance_table,
    parse_table_coordinates,
    create_map_html,
    infer_location,
    extract_map_coords,
    respond,
    chat
)


def test_parse_distance_table_locking_header_only_empty():
    assert parse_distance_table('| A | B | C | D |\n|---|---|---|---|') == []

    table = '| Lat1 | Lon1 | Lat2 | Lon2 |\n|---|---|---|---|\n| 48.8 | 2.3 | 51.5 | -0.1 |'
    assert parse_distance_table(table) == [(48.8, 2.3), (51.5, -0.1)]


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


NON_ASCII_TEXTS = [
    ("accented", "Café"),
    ("CJK", "東京"),
    ("emoji", "🌍"),
    ("RTL", "مرحبا"),
]

@pytest.mark.parametrize("name, text", NON_ASCII_TEXTS)
@pytest.mark.xfail(reason="regex [A-Za-z0-9, ]+ drops non-ASCII characters")
def test_infer_location_non_ascii(name, text):
    assert infer_location(f"for {text}") == text

@pytest.mark.parametrize("name, text", NON_ASCII_TEXTS)
def test_parse_table_coordinates_non_ascii(name, text):
    table = f"| Name | Lat | Lon |\n|---|---|---|\n| {text} | 2.3 | 4.5 |"
    assert parse_table_coordinates(table, 1, 2) == [(2.3, 4.5)]

@pytest.mark.parametrize("name, text", NON_ASCII_TEXTS)
def test_parse_distance_table_non_ascii(name, text):
    table = f"| Lat1 | Lon1 | Lat2 | Lon2 | Name |\n|---|---|---|---|---|\n| 2.3 | 4.5 | 6.7 | 8.9 | {text} |"
    assert parse_distance_table(table) == [(2.3, 4.5), (6.7, 8.9)]

@pytest.mark.parametrize("name, text", NON_ASCII_TEXTS)
def test_extract_map_coords_non_ascii(name, text, mocker):
    mocker.patch.dict("webchat.DEFAULT_TOOL_COORD_PARSERS", {"dummy_tool": (1, 2)})
    table = f"| Name | Lat | Lon |\n|---|---|---|\n| {text} | 2.3 | 4.5 |"
    assert extract_map_coords("dummy_tool", table) == [(2.3, 4.5)]

@pytest.mark.parametrize("name, text", NON_ASCII_TEXTS)
def test_respond_non_ascii(name, text, mocker, tmp_path):
    mock_call = mocker.patch("webchat.call_llm_with_retry")
    mock_invoke = mocker.patch("webchat.registry.invoke", return_value="")
    mocker.patch("webchat.GradioLogHandler", MagicMock())
    mocker.patch("webchat.client", MagicMock())

    mock_message = MagicMock()
    mock_message.content = f"Reply for {text}"
    mock_message.function_call = None
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_call.return_value = mock_response

    reply, _, _, _ = respond(f"message with {text}", [])
    assert f"Reply for {text}" in reply

    test_file = tmp_path / "test.txt"
    test_file.write_text(f"File content with {text}", encoding="utf-8")
    upload_mock = MagicMock()
    upload_mock.name = str(test_file)

    reply2, _, _, _ = respond(f"message with {text}", [], upload_file=upload_mock)
    assert f"Reply for {text}" in reply2

@pytest.mark.parametrize("name, text", NON_ASCII_TEXTS)
def test_chat_non_ascii(name, text, mocker, tmp_path):
    mock_call = mocker.patch("webchat.call_llm_with_retry")
    mock_invoke = mocker.patch("webchat.registry.invoke", return_value="")
    mocker.patch("webchat.GradioLogHandler", MagicMock())
    mocker.patch("webchat.client", MagicMock())

    mock_message = MagicMock()
    mock_message.content = f"Reply for {text}"
    mock_message.function_call = None
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_call.return_value = mock_response

    test_file = tmp_path / "test.txt"
    test_file.write_text(f"File content with {text}", encoding="utf-8")
    upload_mock = MagicMock()
    upload_mock.name = str(test_file)

    history, _, _, _ = chat(f"message with {text}", [], upload_file=upload_mock)
    assert len(history) == 2
    assert history[0]["content"] == f"message with {text}"
    assert history[1]["content"] == f"Reply for {text}"
