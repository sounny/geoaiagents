from file_loaders import load_geojson, load_csv

def test_load_geojson_feature_point_and_invalid():
    res = load_geojson('{"type":"Feature","geometry":{"type":"Point","coordinates":[2.35,48.85]}}')
    assert "| Latitude | Longitude |" in res
    assert "48.85" in res
    assert "2.35" in res

    res_empty = load_geojson('{}')
    assert res_empty.startswith("| Latitude | Longitude |")

    res_bad = load_geojson('{bad')
    assert res_bad.startswith("| Latitude | Longitude |")

def test_load_geojson_feature_collection_one_point():
    fc = '{"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Point","coordinates":[2.35,48.85]},"properties":{}}]}'
    res = load_geojson(fc)
    assert "| Latitude | Longitude |" in res
    assert "48.85" in res
    assert "2.35" in res

def test_load_csv_blank_line_rows_and_header_only_no_numeric_row():
    # Test valid coords
    res_valid = load_csv('Latitude,Longitude\n\n48.8,2.3\n\n')
    assert "48.8" in res_valid
    assert "2.3" in res_valid

    # Test empty
    res_empty = load_csv('')
    assert res_empty == "| Latitude | Longitude |\n|---------:|----------:|"

    # Test header only with \r\n
    res_header_rn = load_csv('Latitude,Longitude\r\n')
    assert "| Latitude | Longitude |" in res_header_rn
    assert "48.8" not in res_header_rn
