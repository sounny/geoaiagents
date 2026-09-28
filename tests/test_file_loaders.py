import pytest
from file_loaders import load_geojson

def test_load_geojson_empty_string():
    with pytest.raises(ValueError, match="GeoJSON is empty"):
        load_geojson("")

def test_load_geojson_whitespace_string():
    with pytest.raises(ValueError, match="GeoJSON is empty"):
        load_geojson("   \n  \t  ")

def test_load_geojson_corrupt_json():
    with pytest.raises(ValueError, match="Corrupt GeoJSON"):
        load_geojson("{ invalid json ")

def test_load_geojson_valid():
    valid_geojson = '{"type": "Point", "coordinates": [-122.4194, 37.7749]}'
    result = load_geojson(valid_geojson)
    assert "| 37.7749 | -122.4194 |" in result
