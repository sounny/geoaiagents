from geoai_cli import _tool_args_for

def test_tool_args_for_totally_unknown_and_file_loaders():
    assert _tool_args_for('totally_unknown_tool', 'payload-x') == {'input': 'payload-x'}
    assert _tool_args_for('load_geojson', '{"type":"Point"}') == {'geojson': '{"type":"Point"}'}
    assert _tool_args_for('load_csv', 'a,b') == {'csv': 'a,b'}
    assert _tool_args_for('load_kml', '<k/>') == {'kml': '<k/>'}
    assert _tool_args_for('not_a_builtin_tool', 'x') == {'input': 'x'}
