import json
import pytest
from file_loaders import load_geojson

def test_load_geojson_point():
    geojson = {
        "type": "Point",
        "coordinates": [2.3522, 48.8566]
    }
    result = load_geojson(json.dumps(geojson))
    assert "| 48.8566 | 2.3522 |" in result

def test_load_geojson_multipoint():
    geojson = {
        "type": "MultiPoint",
        "coordinates": [
            [2.3522, 48.8566],
            [-0.1276, 51.5072]
        ]
    }
    result = load_geojson(json.dumps(geojson))
    assert "| 48.8566 | 2.3522 |" in result
    assert "| 51.5072 | -0.1276 |" in result

def test_load_geojson_polygon():
    geojson = {
        "type": "Polygon",
        "coordinates": [
            [
                [-1.0, -1.0],
                [1.0, -1.0],
                [1.0, 1.0],
                [-1.0, 1.0],
                [-1.0, -1.0]
            ]
        ]
    }
    result = load_geojson(json.dumps(geojson))
    assert "| -1.0 | -1.0 |" in result
    assert "| -1.0 | 1.0 |" in result
    assert "| 1.0 | 1.0 |" in result
    assert "| 1.0 | -1.0 |" in result
    assert result.count("| -1.0 | -1.0 |") == 2

def test_load_geojson_feature_collection_polygon():
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [0.0, 0.0],
                            [1.0, 0.0],
                            [1.0, 1.0],
                            [0.0, 1.0],
                            [0.0, 0.0]
                        ]
                    ]
                }
            }
        ]
    }
    result = load_geojson(json.dumps(geojson))
    assert "| 0.0 | 0.0 |" in result
    assert "| 0.0 | 1.0 |" in result
    assert "| 1.0 | 1.0 |" in result
    assert "| 1.0 | 0.0 |" in result
    assert result.count("| 0.0 | 0.0 |") == 2

def test_load_geojson_invalid_geometry():
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [2.3522, 48.8566]
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[0.0, 0.0], [1.0, 1.0]]
                }
            }
        ]
    }
    result = load_geojson(json.dumps(geojson))
    assert "| 48.8566 | 2.3522 |" in result
    assert "_Skipped invalid inputs:_" in result
    assert "- `LineString` (Unsupported geometry type)" in result

def test_load_geojson_empty():
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    result = load_geojson(json.dumps(geojson))
    assert result == "Error: No coordinates found in GeoJSON data."

def test_load_geojson_invalid_json():
    result = load_geojson("{invalid json")
    assert result == "Error: No coordinates found in GeoJSON data."
