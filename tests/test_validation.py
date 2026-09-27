import pytest
from validation import is_valid_lat_lon, parse_coordinate_pairs, format_invalid_notes

def test_is_valid_lat_lon():
    # Valid coordinates
    assert is_valid_lat_lon(0, 0)
    assert is_valid_lat_lon(90, 180)
    assert is_valid_lat_lon(-90, -180)
    assert is_valid_lat_lon(45.5, -122.6)

    # Invalid coordinates
    assert not is_valid_lat_lon(91, 0)
    assert not is_valid_lat_lon(-91, 0)
    assert not is_valid_lat_lon(0, 181)
    assert not is_valid_lat_lon(0, -181)
    assert not is_valid_lat_lon(100, 200)

def test_parse_coordinate_pairs():
    # Valid inputs
    text_valid = "45.5, -122.6\n34.05, -118.25"
    pairs, invalid = parse_coordinate_pairs(text_valid)
    assert len(pairs) == 2
    assert pairs[0] == (45.5, -122.6)
    assert pairs[1] == (34.05, -118.25)
    assert len(invalid) == 0

    # Valid inputs with semicolons
    text_semi = "45.5, -122.6; 34.05, -118.25"
    pairs, invalid = parse_coordinate_pairs(text_semi)
    assert len(pairs) == 2
    assert pairs[0] == (45.5, -122.6)
    assert pairs[1] == (34.05, -118.25)
    assert len(invalid) == 0

    # Invalid: missing coordinate
    text_missing = "45.5"
    pairs, invalid = parse_coordinate_pairs(text_missing)
    assert len(pairs) == 0
    assert len(invalid) == 1
    assert invalid[0] == ("45.5", "Missing latitude/longitude pair")

    # Invalid: not a number
    text_nan = "abc, def"
    pairs, invalid = parse_coordinate_pairs(text_nan)
    assert len(pairs) == 0
    assert len(invalid) == 1
    assert invalid[0] == ("abc, def", "Not a number")

    # Invalid: out of range
    text_oor = "100, 200"
    pairs, invalid = parse_coordinate_pairs(text_oor)
    assert len(pairs) == 0
    assert len(invalid) == 1
    assert invalid[0] == ("100, 200", "Out of range (-90 <= lat <= 90, -180 <= lon <= 180)")

    # Mixed
    text_mixed = "45.5, -122.6\n100, 200\nabc, def\n34.05, -118.25"
    pairs, invalid = parse_coordinate_pairs(text_mixed)
    assert len(pairs) == 2
    assert len(invalid) == 2
    assert invalid[0] == ("100, 200", "Out of range (-90 <= lat <= 90, -180 <= lon <= 180)")
    assert invalid[1] == ("abc, def", "Not a number")


def test_format_invalid_notes():
    assert format_invalid_notes([]) == ""

    invalid = [("100, 200", "Out of range"), ("abc", "Not a number")]
    result = format_invalid_notes(invalid)
    assert "_Skipped invalid inputs:_" in result
    assert "- `100, 200` (Out of range)" in result
    assert "- `abc` (Not a number)" in result
