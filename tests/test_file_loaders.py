import pytest
from file_loaders import load_geojson

def test_load_geojson_feature_with_point():
    geojson_str = '{"type":"Feature","properties":{},"geometry":{"type":"Point","coordinates":[-0.1278,51.5074]}}'
    expected_table = (
        "| Latitude | Longitude |\n"
        "|---------:|----------:|\n"
        "| 51.5074 | -0.1278 |"
    )
    result = load_geojson(geojson_str)
    assert result == expected_table
