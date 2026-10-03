import pytest
from validation import is_valid_lat_lon, parse_coordinate_pairs, format_invalid_notes

def test_is_valid_lat_lon():
    assert is_valid_lat_lon(0, 0) is True
    assert is_valid_lat_lon(90, 180) is True
    assert is_valid_lat_lon(-90, -180) is True
    assert is_valid_lat_lon(91, 0) is False
    assert is_valid_lat_lon(0, 181) is False
    assert is_valid_lat_lon(-91, 0) is False
    assert is_valid_lat_lon(0, -181) is False

def test_is_valid_lat_lon_inclusive_locked_boundaries():
    assert is_valid_lat_lon(90.0, 0.0) is True
    assert is_valid_lat_lon(-90.0, 180.0) is True
    assert is_valid_lat_lon(0.0, -180.0) is True
    assert is_valid_lat_lon(90.0, 180.0) is True
    assert is_valid_lat_lon(90.001, 0.0) is False
    assert is_valid_lat_lon(0.0, -180.0001) is False

def test_parse_coordinate_pairs():
    text = "0,0\n91,0\nabc,123\n10, 20"
    pairs, invalid = parse_coordinate_pairs(text)
    assert pairs == [(0, 0), (10, 20)]
    assert len(invalid) == 2
    assert invalid[0][0] == "91,0"
    assert invalid[1][0] == "abc,123"

def test_parse_coordinate_pairs_malformed():
    pairs, invalid = parse_coordinate_pairs("10,20\ninvalid\n30,200\n40")

    assert pairs == [(10.0, 20.0)]
    assert len(invalid) == 3
    assert invalid[0] == ("invalid", "Missing latitude/longitude pair")
    assert invalid[1] == ("30,200", "Out of range (-90 <= lat <= 90, -180 <= lon <= 180)")
    assert invalid[2] == ("40", "Missing latitude/longitude pair")

def test_parse_coordinate_pairs_not_a_number():
    pairs, invalid = parse_coordinate_pairs("10,foo")
    assert not pairs
    assert len(invalid) == 1
    assert invalid[0] == ("10,foo", "Not a number")

def test_format_invalid_notes():
    invalid = [("91,0", "Out of range"), ("abc,123", "Not a number")]
    result = format_invalid_notes(invalid)
    assert "Skipped invalid inputs" in result
    assert "`91,0`" in result
    assert "`abc,123`" in result

    formatted = format_invalid_notes([("invalid", "Missing latitude/longitude pair")])
    assert "_Skipped invalid inputs:_" in formatted
    assert "- `invalid` (Missing latitude/longitude pair)" in formatted
