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

import random
from unittest.mock import patch, MagicMock
from types import SimpleNamespace
import webchat

def test_webchat_public_functions_deterministic():
    random.seed(42)

    def mock_call_llm(*args, **kwargs):
        msg = SimpleNamespace(
            content="Mocked deterministic response",
            function_call=None
        )
        return SimpleNamespace(choices=[SimpleNamespace(message=msg)])

    with patch('webchat.call_llm_with_retry', side_effect=mock_call_llm), \
         patch('folium.Map._repr_html_', return_value="<html>mocked map</html>"):

        # 1. infer_location
        out1 = webchat.infer_location("map for Paris")
        out2 = webchat.infer_location("map for Paris")
        assert out1 == out2

        # 2. create_map_html
        pts = [(48.8, 2.3)]
        out1 = webchat.create_map_html(pts)
        out2 = webchat.create_map_html(pts)
        assert out1 == out2

        # 3. parse_table_coordinates
        tbl = "| Lat | Lon |\n|---|---|\n| 48.8 | 2.3 |"
        out1 = webchat.parse_table_coordinates(tbl, 0, 1)
        out2 = webchat.parse_table_coordinates(tbl, 0, 1)
        assert out1 == out2

        # 4. parse_distance_table
        dtbl = "| L1 | L2 | L3 | L4 |\n|---|---|---|---|\n| 1 | 2 | 3 | 4 |"
        out1 = webchat.parse_distance_table(dtbl)
        out2 = webchat.parse_distance_table(dtbl)
        assert out1 == out2

        # 5. extract_map_coords
        out1 = webchat.extract_map_coords("geocode_locations", tbl)
        out2 = webchat.extract_map_coords("geocode_locations", tbl)
        assert out1 == out2

        # 6. run_tool
        func_call = SimpleNamespace(name="geocode_locations", arguments='{"locations": "Paris"}')
        with patch.object(webchat.registry, 'invoke', return_value=tbl):
            out1 = webchat.run_tool(func_call)
            out2 = webchat.run_tool(func_call)
            assert out1 == out2

        # 7. respond & chat require state reset
        def reset_state():
            webchat.messages = [{"role": "system", "content": webchat.system_prompt}]
            webchat.log_history.clear()
            webchat.LAST_MAP_HTML = webchat.create_map_html([(0.0, 0.0)])

        reset_state()
        r1 = webchat.respond("Hello", [])
        reset_state()
        r2 = webchat.respond("Hello", [])
        assert r1 == r2

        reset_state()
        c1 = webchat.chat("Hello", [], None)
        reset_state()
        c2 = webchat.chat("Hello", [], None)
        assert c1 == c2
