import pytest
from file_loaders import load_geojson


def test_load_geojson_feature_linestring():
    geojson_data = '{"type":"Feature","properties":{},"geometry":{"type":"LineString","coordinates":[[2.0,48.0],[3.0,49.0]]}}'
    result = load_geojson(geojson_data)
    assert "| Latitude | Longitude |" in result
    assert "| 48.0 | 2.0 |" in result
    assert "| 49.0 | 3.0 |" in result
    data_rows = [line for line in result.split("\n") if not line.startswith("| Latitude") and not line.startswith("|---")]
    assert len(data_rows) == 2
