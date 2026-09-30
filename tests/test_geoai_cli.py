from geoai_cli import _tool_args_for

def test_tool_args_for_geocode_locations():
    assert _tool_args_for('geocode_locations', 'Paris\nLondon') == {'locations': 'Paris\nLondon'}
