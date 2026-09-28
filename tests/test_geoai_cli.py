import pytest
from geoai_cli import _tool_args_for

def test_tool_args_for_geocode_locations():
    assert _tool_args_for("geocode_locations", "Paris") == {"locations": "Paris"}

def test_tool_args_for_coordinates():
    for tool_name in ["convert_dd_to_dms", "reverse_geocode_coordinates", "calculate_distance"]:
        assert _tool_args_for(tool_name, "48.85,2.35") == {"coordinates": "48.85,2.35"}

def test_tool_args_for_text_fields():
    assert _tool_args_for("load_geojson", '{"type": "Point"}') == {"geojson": '{"type": "Point"}'}
    assert _tool_args_for("load_kml", "<kml></kml>") == {"kml": "<kml></kml>"}
    assert _tool_args_for("load_csv", "lat,lon\n1,1") == {"csv": "lat,lon\n1,1"}

def test_tool_args_for_fetch_geo_boundaries():
    assert _tool_args_for("fetch_geo_boundaries", "USA") == {"iso": "USA", "adm": "ADM0"}
    assert _tool_args_for("fetch_geo_boundaries", "USA", adm="ADM1") == {"iso": "USA", "adm": "ADM1"}

def test_tool_args_for_unknown():
    assert _tool_args_for("unknown_tool", "payload") == {"input": "payload"}
