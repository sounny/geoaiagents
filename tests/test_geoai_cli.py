from geoai_cli import _tool_args_for

def test_tool_args_for_fetch_geo_boundaries():
    assert _tool_args_for('fetch_geo_boundaries', 'FRA', adm='ADM1') == {'iso': 'FRA', 'adm': 'ADM1'}

def test_tool_args_for_geocode_locations():
    assert _tool_args_for('geocode_locations', 'Paris') == {'locations': 'Paris'}
