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
    assert is_valid_lat_lon(90, 0) is True
    assert is_valid_lat_lon(-90, 0) is True

def test_is_valid_lat_lon_locked_boundaries():
    assert is_valid_lat_lon(90.0, 0.0) is True
    assert is_valid_lat_lon(-90.0, 180.0) is True
    assert is_valid_lat_lon(0.0, -180.0) is True
    assert is_valid_lat_lon(90.001, 0.0) is False
    assert is_valid_lat_lon(0.0, -180.0001) is False
    assert is_valid_lat_lon(12.5, -180.0001) is False

def test_is_valid_lat_lon_nan_inf():
    assert is_valid_lat_lon(float("nan"), 0) is False
    assert is_valid_lat_lon(0, float("nan")) is False
    assert is_valid_lat_lon(float("inf"), 0) is False
    assert is_valid_lat_lon(0, float("inf")) is False
    assert is_valid_lat_lon(float("-inf"), 0) is False
    assert is_valid_lat_lon(0, float("-inf")) is False

def test_parse_coordinate_pairs():
    text = "0,0\n91,0\nabc,123\n10, 20"
    pairs, invalid = parse_coordinate_pairs(text)
    assert pairs == [(0, 0), (10, 20)]
    assert len(invalid) == 2
    assert invalid[0][0] == "91,0"
    assert invalid[1][0] == "abc,123"

def test_parse_coordinate_pairs_malformed():
    pairs, invalid = parse_coordinate_pairs("10,20\ninvalid\n30,200\n40\n120, 45")

    assert pairs == [(10.0, 20.0)]
    assert len(invalid) == 4
    assert invalid[0] == ("invalid", "Missing latitude/longitude pair")
    assert invalid[1] == ("30,200", "Out of range (-90 <= lat <= 90, -180 <= lon <= 180)")
    assert invalid[2] == ("40", "Missing latitude/longitude pair")
    assert invalid[3] == ("120, 45", "Out of range (-90 <= lat <= 90, -180 <= lon <= 180)")

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

def test_parse_coordinate_pairs_space_separated_locked():
    # Test valid space-separated and semicolon-delimited coordinates
    valid_text = "35.6762 139.6503; 34.6937 135.5023"
    pairs, invalid = parse_coordinate_pairs(valid_text)
    assert pairs == [(35.6762, 139.6503), (34.6937, 135.5023)]
    assert not invalid

    # Test invalid coordinates (out of range lat)
    pairs1, invalid1 = parse_coordinate_pairs("91 0")
    assert not pairs1
    assert len(invalid1) == 1
    assert "Out of range" in invalid1[0][1]

    # Test invalid coordinates (out of range lon)
    pairs2, invalid2 = parse_coordinate_pairs("0 181")
    assert not pairs2
    assert len(invalid2) == 1
    assert "Out of range" in invalid2[0][1]

def test_swap_axis_order():
    try:
        from validation import swap_axis_order
    except ImportError:
        pytest.xfail("swap_axis_order helper is missing")

    # Assert (lat, lon) to (lon, lat) swaps coordinates
    assert swap_axis_order((10.0, 20.0)) == (20.0, 10.0)

    # Assert extra dimensions are preserved
    assert swap_axis_order((10.0, 20.0, 30.0)) == (20.0, 10.0, 30.0)
    assert swap_axis_order((10.0, 20.0, 30.0, 40.0)) == (20.0, 10.0, 30.0, 40.0)

def test_format_invalid_notes_iterable_non_empty():
    invalid = [("91,0", "Out of range"), ("abc,123", "Not a number")]
    assert format_invalid_notes(iter(invalid)) == format_invalid_notes(invalid)

@pytest.mark.xfail(strict=True, raises=AssertionError, reason="Bug: empty iterators evaluate as truthy, returning the header instead of an empty string")
def test_format_invalid_notes_iterable_empty():
    assert format_invalid_notes(iter([])) == format_invalid_notes([])
