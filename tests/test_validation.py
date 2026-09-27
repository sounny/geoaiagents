import pytest
from validation import is_valid_lat_lon, parse_coordinate_pairs, format_invalid_notes

def test_is_valid_lat_lon():
    assert is_valid_lat_lon(45.0, 90.0) is True
    assert is_valid_lat_lon(-90.0, -180.0) is True
    assert is_valid_lat_lon(90.0, 180.0) is True
    assert is_valid_lat_lon(91.0, 0.0) is False
    assert is_valid_lat_lon(0.0, 181.0) is False
    assert is_valid_lat_lon(-91.0, 0.0) is False
    assert is_valid_lat_lon(0.0, -181.0) is False

def test_parse_coordinate_pairs_valid():
    pairs, invalid = parse_coordinate_pairs("45.0, 90.0\n -10, 20")
    assert pairs == [(45.0, 90.0), (-10.0, 20.0)]
    assert invalid == []

def test_parse_coordinate_pairs_invalid():
    pairs, invalid = parse_coordinate_pairs("45.0\n foo, bar\n 91.0, 0.0\n 45.0, 90.0")
    assert pairs == [(45.0, 90.0)]
    assert len(invalid) == 3
    assert invalid[0] == ("45.0", "Missing latitude/longitude pair")
    assert invalid[1] == ("foo, bar", "Not a number")
    assert invalid[2] == ("91.0, 0.0", "Out of range (-90 <= lat <= 90, -180 <= lon <= 180)")

def test_format_invalid_notes():
    invalid = [("foo", "Not a number"), ("91.0, 0.0", "Out of range (-90 <= lat <= 90, -180 <= lon <= 180)")]
    output = format_invalid_notes(invalid)
    assert "_Skipped invalid inputs:_" in output
    assert "- `foo` (Not a number)" in output
    assert "- `91.0, 0.0` (Out of range (-90 <= lat <= 90, -180 <= lon <= 180))" in output

    assert format_invalid_notes([]) == ""
