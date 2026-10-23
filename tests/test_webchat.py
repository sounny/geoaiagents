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

@pytest.mark.xfail(reason="Regex in infer_location does not support non-Latin characters", strict=False)
def test_infer_location_non_latin():
    from webchat import infer_location
    assert infer_location("map for 🌍") == "🌍"
    assert infer_location("map for 東京") == "東京"
    assert infer_location("map for São Paulo") == "São Paulo"

@pytest.mark.xfail(reason="Bug in infer_location propagates to chat, returning partial/incorrect table instead of geocoding all targets", strict=False)
def test_chat_non_latin_auto_geocode(mocker):
    from webchat import chat
    from types import SimpleNamespace

    mock_llm = mocker.patch("webchat.call_llm_with_retry")
    mock_llm.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="Reply for 🌍", function_call=None))]
    )

    mock_invoke = mocker.patch("webchat.registry.invoke")
    mock_invoke.return_value = "| Location | Latitude | Longitude |\n|---|---|---|\n| S | -23.5 | -46.6 |"

    history, map_html, logs, table = chat("map for São Paulo, 東京, and 🌍", [], None)

    # Assert the correct/expected behavior which currently fails
    assert table == "| Location | Latitude | Longitude |\n|---|---|---|\n| São Paulo, 東京, and 🌍 | -23.5 | -46.6 |"
