import pytest
import file_loaders

def test_load_geojson_linestring():
    # Verify exact match with Paris then London coordinates order
    geojson = '{"type":"LineString","coordinates":[[2.3522,48.8566],[-0.1278,51.5074]]}'
    result = file_loaders.load_geojson(geojson)
    assert "| 48.8566 | 2.3522 |" in result
    assert "| 51.5074 | -0.1278 |" in result

    # check order
    paris_idx = result.find("| 48.8566 |")
    london_idx = result.find("| 51.5074 |")
    assert paris_idx < london_idx
