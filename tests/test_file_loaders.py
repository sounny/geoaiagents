import pytest
from file_loaders import load_kml

def test_load_kml_invalid_inputs():
    invalid_inputs = ['<not>valid', '']
    for val in invalid_inputs:
        result = load_kml(val)
        assert result.startswith('| Latitude | Longitude |')
        lines = result.strip().split('\n')
        assert len(lines) == 2

def test_load_kml_empty_coordinates_node():
    empty_kml = '<?xml version="1.0"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document><Placemark><Point><coordinates></coordinates></Point></Placemark></Document></kml>'
    result_empty = load_kml(empty_kml)
    assert '| Latitude | Longitude |' in result_empty

    # check that there are no numeric data rows.
    # usually there are 2 lines: header and separator
    lines = result_empty.strip().split('\n')
    assert len(lines) == 2

    valid_kml = '<?xml version="1.0"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document><Placemark><Point><coordinates>2.35,48.85,0</coordinates></Point></Placemark></Document></kml>'
    result_valid = load_kml(valid_kml)
    assert '48.85' in result_valid
    assert '2.35' in result_valid
