from file_loaders import load_geojson

def test_load_geojson_malformed_string_returns_empty_table():
    result = load_geojson('not-json{')
    assert '| Latitude | Longitude |' in result
    assert len(result.strip().split('\n')) == 2

def test_load_geojson_pure_point_parsing_coordinates_order():
    result = load_geojson('{"type":"Point","coordinates":[2.35,48.85]}')
    assert '48.85' in result
    assert '2.35' in result
