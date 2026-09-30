import pytest
from file_loaders import load_geojson, load_csv, load_kml, fetch_geo_boundaries

def test_load_geojson_point():
    geojson_str = '{"type":"Feature","geometry":{"type":"Point","coordinates":[2.3522,48.8566]},"properties":{}}'
    result = load_geojson(geojson_str)
    assert "| 48.8566 | 2.3522 |" in result
    assert "invalid" not in result.lower()

def test_load_geojson_null_geometry():
    geojson_str = '{"type":"Feature","geometry":null,"properties":{}}'
    result = load_geojson(geojson_str)
    assert "_Skipped invalid inputs:_" in result
    assert "- `null` (Null geometry)" in result

def test_load_geojson_missing_geometry():
    geojson_str = '{"type":"Feature","properties":{}}'
    result = load_geojson(geojson_str)
    assert "_Skipped invalid inputs:_" in result
    assert "- `null` (Null geometry)" in result

def test_load_geojson_unsupported_geometry():
    geojson_str = '{"type":"Feature","geometry":{"type":"LineString","coordinates":[[0,0],[1,1]]},"properties":{}}'
    result = load_geojson(geojson_str)
    assert "_Skipped invalid inputs:_" in result
    assert "- `LineString` (Unsupported geometry)" in result

def test_load_geojson_feature_collection():
    geojson_str = '{"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Point","coordinates":[1,2]}},{"type":"Feature","geometry":null},{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[0,0],[1,1],[1,0],[0,0]]]}}]}'
    result = load_geojson(geojson_str)
    assert "| 2 | 1 |" in result
    assert "_Skipped invalid inputs:_" in result
    assert "- `null` (Null geometry)" in result
    assert "- `Polygon` (Unsupported geometry)" in result
