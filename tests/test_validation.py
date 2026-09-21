import pytest
from validation import is_valid_lat_lon, parse_coordinate_pairs, format_invalid_notes

def test_is_valid_lat_lon():
    assert is_valid_lat_lon(0, 0)
    assert is_valid_lat_lon(90, 180)
    assert is_valid_lat_lon(-90, -180)
    assert not is_valid_lat_lon(91, 0)
    assert not is_valid_lat_lon(-91, 0)
    assert not is_valid_lat_lon(0, 181)
    assert not is_valid_lat_lon(0, -181)

def test_parse_coordinate_pairs():
    text = "40.7128, -74.0060\n34.0522, -118.2437"
    pairs, invalid = parse_coordinate_pairs(text)
    assert len(pairs) == 2
    assert pairs[0] == (40.7128, -74.0060)
    assert pairs[1] == (34.0522, -118.2437)
    assert len(invalid) == 0

    text_invalid = "40.7128, -74.0060\n91, 0\nbad, data"
    pairs, invalid = parse_coordinate_pairs(text_invalid)
    assert len(pairs) == 1
    assert len(invalid) == 2
    assert "Out of range" in invalid[0][1]
    assert "Not a number" in invalid[1][1]

def test_format_invalid_notes():
    assert format_invalid_notes([]) == ""
    invalid = [("91, 0", "Out of range")]
    formatted = format_invalid_notes(invalid)
    assert "Skipped invalid inputs" in formatted
    assert "91, 0" in formatted
