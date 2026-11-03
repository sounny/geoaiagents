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

from webchat import extract_map_coords, respond
from unittest.mock import patch, Mock
import logging

@pytest.mark.xfail(reason="extract_map_coords uses DEFAULT_TOOL_COORD_PARSERS which is case-sensitive, so extract_map_coords does not handle tool names in UPPER or Mixed case")
def test_extract_map_coords_upper_case():
    table = '| A | B | C | D |\n|---|---|---|---|\n| 48.8 | 2.3 | 51.5 | -0.1 |'
    assert extract_map_coords("DISTANCE", table) == [(48.8, 2.3), (51.5, -0.1)]
    assert extract_map_coords("CALCULATE_DISTANCE", table) == [(48.8, 2.3), (51.5, -0.1)]
    assert extract_map_coords("Geocode_Locations", "| Location | Address | Lat | Lon |\n|---|---|---|---|\n| Valid 1 | Addr | 51.5074 | -0.1278 |") == [(51.5074, -0.1278)]

@patch("webchat.call_llm_with_retry")
@pytest.mark.xfail(reason="respond uses ToolRegistry which is case-sensitive, so respond fails to find the correct tool when function_call.name is UPPER or Mixed case")
def test_respond_upper_case(mock_call_llm, caplog):
    caplog.set_level(logging.INFO)
    mock_resp = Mock()
    mock_msg = Mock()
    mock_msg.function_call = Mock(name="CALCULATE_DISTANCE", arguments='{"coordinates": "48.8,2.3,51.5,-0.1"}')
    mock_msg.function_call.name = "CALCULATE_DISTANCE"
    mock_msg.content = "I calculated the distance"
    mock_resp.choices = [Mock(message=mock_msg)]

    mock_resp2 = Mock()
    mock_resp2.choices = [Mock(message=Mock(content="Here is the distance map"))]
    mock_call_llm.side_effect = [mock_resp, mock_resp2]

    reply, html, logs, table = respond("how far?", [])
    assert table != ""
    assert "CALCULATE_DISTANCE" in table
