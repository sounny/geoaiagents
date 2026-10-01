import pytest
from validation import is_valid_lat_lon, parse_coordinate_pairs, format_invalid_notes

def test_is_valid_lat_lon_poles_and_antimeridian():
    assert is_valid_lat_lon(90, 0) is True
    assert is_valid_lat_lon(-90, 0) is True
    assert is_valid_lat_lon(0, 180) is True
    assert is_valid_lat_lon(0, -180) is True
    assert is_valid_lat_lon(90.0001, 0) is False
    assert is_valid_lat_lon(-90.0001, 0) is False
    assert is_valid_lat_lon(0, 180.0001) is False
    assert is_valid_lat_lon(0, -180.0001) is False

def test_is_valid_lat_lon_boundaries():
    assert is_valid_lat_lon(90.0, 180.0) is True
    assert is_valid_lat_lon(90.1, 0) is False
    assert is_valid_lat_lon(-90.1, 0) is False
    assert is_valid_lat_lon(0, 180.1) is False
    assert is_valid_lat_lon(0, -180.1) is False

def test_parse_coordinate_pairs_newline_separated():
    pairs, invalid = parse_coordinate_pairs("48.8566,2.3522\n51.5074,-0.1278")
    assert pairs == [(48.8566, 2.3522), (51.5074, -0.1278)]
    assert invalid == []

def test_parse_coordinate_pairs_semicolon_delimited():
    valid_pairs, invalid_entries = parse_coordinate_pairs("48.8,2.3; 51.5,-0.12")
    assert valid_pairs == [(48.8, 2.3), (51.5, -0.12)]
    assert invalid_entries == []

def test_parse_coordinate_pairs_tab_separated():
    pairs, invalid = parse_coordinate_pairs("48.8566\t2.3522")
    assert pairs == [(48.8566, 2.3522)]
    assert invalid == []

def test_parse_coordinate_pairs_out_of_range():
    pairs, invalid = parse_coordinate_pairs("91,0")
    assert pairs == []
    assert len(invalid) == 1
    assert invalid[0][0] == "91,0"
    assert "Out of range" in invalid[0][1]

def test_parse_coordinate_pairs_not_a_number():
    pairs, invalid = parse_coordinate_pairs("foo,bar")
    assert pairs == []
    assert len(invalid) == 1
    assert invalid[0][0] == "foo,bar"
    assert invalid[0][1] == "Not a number"

def test_parse_coordinate_pairs_missing_pair():
    pairs, invalid = parse_coordinate_pairs("48.8566")
    assert pairs == []
    assert len(invalid) == 1
    assert invalid[0][0] == "48.8566"
    assert invalid[0][1] == "Missing latitude/longitude pair"

def test_format_invalid_notes_empty():
    assert format_invalid_notes([]) == ""
    assert format_invalid_notes(()) == ""

def test_format_invalid_notes_out_of_range():
    result = format_invalid_notes([("91,0", "Out of range")])
    assert "_Skipped invalid inputs:_" in result
    assert "- `91,0` (Out of range)" in result

def test_parse_coordinate_pairs_generic():
    text = "0,0\n91,0\nabc,123\n10, 20"
    pairs, invalid = parse_coordinate_pairs(text)
    assert pairs == [(0, 0), (10, 20)]
    assert len(invalid) == 2
    assert invalid[0][0] == "91,0"
    assert invalid[1][0] == "abc,123"

def test_format_invalid_notes_generic():
    formatted = format_invalid_notes([("invalid", "Missing latitude/longitude pair")])
    assert "_Skipped invalid inputs:_" in formatted
    assert "- `invalid` (Missing latitude/longitude pair)" in formatted
