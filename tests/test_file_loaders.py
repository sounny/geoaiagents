import pytest
import requests
from file_loaders import fetch_geo_boundaries, load_geojson, load_csv, load_kml, _table

def test_fetch_geo_boundaries_network_error(monkeypatch):
    def mock_get(*args, **kwargs):
        raise requests.exceptions.RequestException("Mocked network error")
    monkeypatch.setattr(requests, "get", mock_get)
    result = fetch_geo_boundaries('FRA')
    assert result.startswith("| Latitude | Longitude |")
    lines = result.split('\n')
    assert len(lines) == 2
    assert '48.85' not in result

def test_load_geojson_malformed_and_valid_point():
    malformed_result = load_geojson('not-json{')
    assert malformed_result.startswith("| Latitude | Longitude |")
    assert len(malformed_result.split('\n')) == 2

    valid_point = '{"type":"Point","coordinates":[2.35,48.85]}'
    valid_result = load_geojson(valid_point)
    assert '48.85' in valid_result
    assert '2.35' in valid_result

def test_load_csv_empty_and_header_only():
    empty_result = load_csv('')
    assert empty_result.startswith("| Latitude | Longitude |")
    assert len(empty_result.split('\n')) == 2

    header_result = load_csv('Latitude,Longitude\n\n')
    assert header_result.startswith("| Latitude | Longitude |")
    assert len(header_result.split('\n')) == 2

def test_load_kml_invalid_and_valid_point():
    invalid_result = load_kml('<not>valid')
    assert invalid_result.startswith("| Latitude | Longitude |")
    assert len(invalid_result.split('\n')) == 2

    empty_result = load_kml('')
    assert empty_result.startswith("| Latitude | Longitude |")
    assert len(empty_result.split('\n')) == 2

    valid_point = '<kml xmlns:k="http://www.opengis.net/kml/2.2"><k:coordinates>2.35,48.85,0</k:coordinates></kml>'
    valid_result = load_kml(valid_point)
    assert '48.85' in valid_result
    assert '2.35' in valid_result

def test_table_empty_list_and_valid_coords():
    empty_result = _table([])
    lines = empty_result.split('\n')
    assert len(lines) == 2
    assert lines[0] == "| Latitude | Longitude |"

    valid_result = _table([(48.8566, 2.3522)])
    valid_lines = valid_result.split('\n')
    assert len(valid_lines) == 3
    assert '48.8566' in valid_lines[2]
    assert '2.3522' in valid_lines[2]
