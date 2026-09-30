import pytest
from file_loaders import load_geojson, load_kml, load_csv

def test_load_geojson_empty_feature_collection():
    result = load_geojson('{"type":"FeatureCollection","features":[]}')
    assert result == "Error: No coordinates found in GeoJSON data."

def test_load_geojson_invalid():
    result = load_geojson('not a json')
    assert result == "Error: No coordinates found in GeoJSON data."
