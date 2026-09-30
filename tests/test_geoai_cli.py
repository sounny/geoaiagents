from geoai_cli import _tool_args_for

def test_tool_args_for_calculate_distance():
    assert _tool_args_for('calculate_distance', '48.8,2.3,51.5,-0.1') == {'coordinates': '48.8,2.3,51.5,-0.1'}

def test_tool_args_for_reverse_geocode_coordinates():
    assert _tool_args_for('reverse_geocode_coordinates', '1,2') == {'coordinates': '1,2'}

def test_tool_args_for_convert_dd_to_dms():
    assert _tool_args_for('convert_dd_to_dms', '1,2') == {'coordinates': '1,2'}
