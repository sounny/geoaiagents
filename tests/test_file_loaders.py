import pytest
from file_loaders import load_geojson

def test_load_geojson_point():
    geojson_data = '{"type":"Point","coordinates":[2.3522,48.8566]}'
    result = load_geojson(geojson_data)

    expected = "\n".join([
        "| Latitude | Longitude |",
        "|---------:|----------:|",
        "| 48.8566 | 2.3522 |"
    ])

    assert result == expected
