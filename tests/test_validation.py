import math
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


def test_is_valid_lat_lon_bad_types():
    with pytest.raises(TypeError):
        is_valid_lat_lon(None, 0) # type: ignore
    with pytest.raises(TypeError):
        is_valid_lat_lon(0, None) # type: ignore
    with pytest.raises(TypeError):
        is_valid_lat_lon("90", 0) # type: ignore
    with pytest.raises(TypeError):
        is_valid_lat_lon(0, "180") # type: ignore

def test_is_valid_lat_lon_exceeding_bounds():
    assert is_valid_lat_lon(90.000001, 0) is False
    assert is_valid_lat_lon(-90.000001, 0) is False
    assert is_valid_lat_lon(0, 180.000001) is False
    assert is_valid_lat_lon(0, -180.000001) is False
    assert is_valid_lat_lon(math.inf, 0) is False
    assert is_valid_lat_lon(0, math.inf) is False
    assert is_valid_lat_lon(-math.inf, 0) is False
    assert is_valid_lat_lon(0, -math.inf) is False
    assert is_valid_lat_lon(math.nan, 0) is False
    assert is_valid_lat_lon(0, math.nan) is False

def test_parse_coordinate_pairs_empty_and_whitespace():
    pairs, invalid = parse_coordinate_pairs("")
    assert not pairs
    assert not invalid

    pairs, invalid = parse_coordinate_pairs(None) # type: ignore
    assert not pairs
    assert not invalid

    pairs, invalid = parse_coordinate_pairs("   \n  \t ")
    assert not pairs
    assert not invalid

def test_parse_coordinate_pairs_inf_and_nan():
    pairs, invalid = parse_coordinate_pairs("inf, 0\n0, nan\n-inf, -inf")
    assert not pairs
    assert len(invalid) == 3
    assert invalid[0] == ("inf, 0", "Out of range (-90 <= lat <= 90, -180 <= lon <= 180)")
    assert invalid[1] == ("0, nan", "Out of range (-90 <= lat <= 90, -180 <= lon <= 180)")
    assert invalid[2] == ("-inf, -inf", "Out of range (-90 <= lat <= 90, -180 <= lon <= 180)")

def test_format_invalid_notes_empty():
    assert format_invalid_notes([]) == ""
