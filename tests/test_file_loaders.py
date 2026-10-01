import pytest
from file_loaders import load_csv, load_geojson, load_kml, _table

def test_load_csv_missing_latitude_column_path():
    result = load_csv('name,x\nParis,1')
    assert result.startswith('| Latitude | Longitude |')
    assert len(result.splitlines()) == 2

def test_load_csv_valid_parse_path():
    result = load_csv('Latitude,Longitude\n48.8,2.3')
    assert '48.8' in result
    assert '2.3' in result

def test_load_csv_empty_string_and_header_only():
    result_empty = load_csv('')
    assert result_empty.startswith('| Latitude | Longitude |')
    assert len(result_empty.splitlines()) == 2

    result_header = load_csv('Latitude,Longitude\n\n')
    assert result_header.startswith('| Latitude | Longitude |')
    assert len(result_header.splitlines()) == 2

def test_table_empty_and_valid():
    result_empty = _table([])
    assert result_empty.startswith('| Latitude | Longitude |')
    assert len(result_empty.splitlines()) == 2

    result_valid = _table([(48.8566, 2.3522)])
    lines = result_valid.splitlines()
    assert len(lines) == 3
    assert '48.8566' in lines[2]
    assert '2.3522' in lines[2]

def test_load_geojson_invalid_and_valid():
    result_invalid = load_geojson('not-json{')
    assert result_invalid.startswith('| Latitude | Longitude |')
    assert len(result_invalid.splitlines()) == 2

    result_valid = load_geojson('{"type":"Point","coordinates":[2.35,48.85]}')
    assert '48.85' in result_valid
    assert '2.35' in result_valid

def test_load_kml_invalid_and_valid():
    result_invalid = load_kml('<not>valid')
    assert result_invalid.startswith('| Latitude | Longitude |')
    assert len(result_invalid.splitlines()) == 2

    result_empty = load_kml('')
    assert result_empty.startswith('| Latitude | Longitude |')
    assert len(result_empty.splitlines()) == 2

    kml_str = '''<?xml version="1.0" encoding="UTF-8"?>
    <kml xmlns="http://www.opengis.net/kml/2.2">
      <Placemark>
        <Point>
          <coordinates>2.35,48.85,0</coordinates>
        </Point>
      </Placemark>
    </kml>'''
    result_valid = load_kml(kml_str)
    assert '48.85' in result_valid
    assert '2.35' in result_valid
