import pytest
from file_loaders import load_geojson

def test_load_geojson_feature_point():
    valid_geojson = '{"type":"Feature","geometry":{"type":"Point","coordinates":[2.35,48.85]}}'
    res = load_geojson(valid_geojson)
    assert '| Latitude | Longitude |' in res
    assert '48.85' in res
    assert '2.35' in res
    lines = res.strip().split('\n')
    assert len(lines) >= 3
    data_row = lines[2]
    parts = [p.strip() for p in data_row.split('|') if p.strip()]
    assert parts[0] == '48.85'
    assert parts[1] == '2.35'

def test_load_geojson_invalid_json():
    res1 = load_geojson('{}')
    assert '| Latitude | Longitude |' in res1
    assert len(res1.strip().split('\n')) == 2

    res2 = load_geojson('{bad')
    assert '| Latitude | Longitude |' in res2
    assert len(res2.strip().split('\n')) == 2
