import pytest
from file_loaders import load_geojson
import validation

def test_load_geojson_multipoint():
    geojson_str = '{"type":"MultiPoint","coordinates":[[2.3522,48.8566],[-0.1278,51.5074]]}'
    res = load_geojson(geojson_str)
    assert "| 48.8566 | 2.3522 |" in res
    assert "| 51.5074 | -0.1278 |" in res
    # Ensure they are in the correct order
    assert res.find("| 48.8566") < res.find("| 51.5074")

def test_load_geojson_rejects_non_points():
    geojson_str = '{"type":"LineString","coordinates":[[2.3522,48.8566],[-0.1278,51.5074]]}'
    res = load_geojson(geojson_str)
    assert "| 48.8566" not in res
    assert "_Skipped invalid inputs:_" in res
    assert "- `LineString` (Unsupported geometry type)" in res
