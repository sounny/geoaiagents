from geoai_cli import _tool_args_for

def test_tool_args_for_fetch_geo_boundaries_adm2():
    assert _tool_args_for('fetch_geo_boundaries', 'FRA', 'ADM2') == {'iso': 'FRA', 'adm': 'ADM2'}
