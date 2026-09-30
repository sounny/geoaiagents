import pytest
from file_loaders import load_geojson

def test_load_geojson_single_point_featurecollection():
    geojson_str = '{"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"type":"Point","coordinates":[2.3522,48.8566]}}]}'
    result = load_geojson(geojson_str)

    # Extract data lines
    lines = result.split('\n')
    data_lines = [line for line in lines if line and not line.startswith('| Latitude') and not line.startswith('|---')]

    # Verify exactly one Latitude/Longitude data row
    assert len(data_lines) == 1
    assert '| 48.8566 | 2.3522 |' in data_lines[0]
