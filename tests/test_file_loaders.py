import pytest
from file_loaders import load_geojson, _table

def test_load_geojson_valid():
    valid_geojson = '{"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": {"type": "Point", "coordinates": [10.0, 20.0]}, "properties": {}}]}'
    result = load_geojson(valid_geojson)
    assert "| 20.0 | 10.0 |" in result

def test_load_geojson_empty_feature_collection():
    empty_fc = '{"type": "FeatureCollection", "features": []}'
    result = load_geojson(empty_fc)
    assert result == _table([])

def test_load_geojson_empty_string():
    with pytest.raises(ValueError, match="Empty GeoJSON string"):
        load_geojson("")

    with pytest.raises(ValueError, match="Empty GeoJSON string"):
        load_geojson("   ")

def test_load_geojson_invalid_json():
    with pytest.raises(ValueError, match="Invalid GeoJSON:"):
        load_geojson("{invalid json}")

def test_load_geojson_non_object_geometry_string():
    invalid_geom = '{"type": "Feature", "geometry": "point", "properties": {}}'
    with pytest.raises(ValueError, match="Feature geometry must be an object or null"):
        load_geojson(invalid_geom)

def test_load_geojson_non_object_geometry_number():
    invalid_geom = '{"type": "Feature", "geometry": 123, "properties": {}}'
    with pytest.raises(ValueError, match="Feature geometry must be an object or null"):
        load_geojson(invalid_geom)

def test_load_geojson_non_object_geometry_list():
    invalid_geom = '{"type": "Feature", "geometry": [10.0, 20.0], "properties": {}}'
    with pytest.raises(ValueError, match="Feature geometry must be an object or null"):
        load_geojson(invalid_geom)

def test_load_geojson_null_geometry():
    valid_geom = '{"type": "Feature", "geometry": null, "properties": {}}'
    result = load_geojson(valid_geom)
    assert result == _table([])
