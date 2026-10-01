from geoai_cli import _tool_args_for

def test_tool_args_for_fetch_geo_boundaries():
    assert _tool_args_for('fetch_geo_boundaries', 'fra', 'ADM1') == {'iso': 'fra', 'adm': 'ADM1'}
    assert _tool_args_for('fetch_geo_boundaries', 'DEU') == {'iso': 'DEU', 'adm': 'ADM0'}

def test_tool_args_for_geocode_locations():
    assert _tool_args_for('geocode_locations', 'Paris') == {'locations': 'Paris'}
