import pytest
import math
from distance import _parse_distance_pairs, _haversine_km, calculate_distance

def test_parse_distance_pairs():
    # Valid
    text_valid = "45.5, -122.6, 34.05, -118.25"
    pairs, invalid = _parse_distance_pairs(text_valid)
    assert len(pairs) == 1
    assert pairs[0] == (45.5, -122.6, 34.05, -118.25)
    assert len(invalid) == 0

    # Multiple
    text_multi = "0,0,1,1\n2,2,3,3"
    pairs, invalid = _parse_distance_pairs(text_multi)
    assert len(pairs) == 2
    assert pairs[0] == (0, 0, 1, 1)
    assert pairs[1] == (2, 2, 3, 3)

    # Invalid: missing coordinate
    text_missing = "45.5, -122.6, 34.05"
    pairs, invalid = _parse_distance_pairs(text_missing)
    assert len(pairs) == 0
    assert len(invalid) == 1
    assert "Expected lat1, lon1, lat2, lon2" in invalid[0][1]

    # Invalid: NaN
    text_nan = "a, b, c, d"
    pairs, invalid = _parse_distance_pairs(text_nan)
    assert len(pairs) == 0
    assert len(invalid) == 1
    assert "Not a number" in invalid[0][1]

    # Invalid: point A out of range
    text_oor_a = "100, 0, 0, 0"
    pairs, invalid = _parse_distance_pairs(text_oor_a)
    assert len(pairs) == 0
    assert len(invalid) == 1
    assert "Point A out of range" in invalid[0][1]

    # Invalid: point B out of range
    text_oor_b = "0, 0, 100, 0"
    pairs, invalid = _parse_distance_pairs(text_oor_b)
    assert len(pairs) == 0
    assert len(invalid) == 1
    assert "Point B out of range" in invalid[0][1]


def test_haversine_km():
    # Distance to self should be 0
    assert _haversine_km(0, 0, 0, 0) == 0.0
    assert _haversine_km(45.5, -122.6, 45.5, -122.6) == 0.0

    # Known distance (approximate)
    # Portland (45.52, -122.68) to Seattle (47.61, -122.33) is ~ 233 km
    dist = _haversine_km(45.52, -122.68, 47.61, -122.33)
    assert math.isclose(dist, 233.9, rel_tol=0.01)

def test_calculate_distance():
    text_valid = "45.52, -122.68, 47.61, -122.33"
    result = calculate_distance(text_valid)
    assert "| Point A Lat | Point A Lon | Point B Lat | Point B Lon | Distance (km) | Distance (mi) |" in result
    assert "45.520000" in result
    assert "47.610000" in result
    assert "233.9" in result # km

    # Invalid input
    result_invalid = calculate_distance("abc")
    assert "No valid coordinate pairs provided." in result_invalid
    assert "_Skipped invalid inputs:_" in result_invalid
