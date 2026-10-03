import pytest
from file_loaders import load_geojson

def test_load_geojson_multilinestring():
    geojson_data = '{"type":"MultiLineString","coordinates":[[[2.35,48.85],[-0.12,51.50]]]}'
    result = load_geojson(geojson_data)
    expected_lines = [
        "| Latitude | Longitude |",
        "|---------:|----------:|",
        "| 48.85 | 2.35 |",
        "| 51.5 | -0.12 |"
    ]
    expected = "\n".join(expected_lines)
    assert result == expected
