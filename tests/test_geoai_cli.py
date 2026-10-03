from geoai_cli import _tool_args_for

def test_tool_args_for_fetch_geo_boundaries_adm0():
    assert _tool_args_for('fetch_geo_boundaries', 'USA', 'ADM0') == {'iso': 'USA', 'adm': 'ADM0'}
    assert _tool_args_for('fetch_geo_boundaries', 'usa', 'ADM0') == {'iso': 'usa', 'adm': 'ADM0'}
