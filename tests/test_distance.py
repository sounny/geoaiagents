import pytest
from distance import _haversine_km, _parse_distance_pairs, calculate_distance
import math

def test_haversine_km():
    # Distance between New York (40.7128, -74.0060) and London (51.5074, -0.1278)
    # is roughly 5570 km.
    dist = _haversine_km(40.7128, -74.0060, 51.5074, -0.1278)
    assert 5560 < dist < 5580

def test_parse_distance_pairs():
    # Valid pair
    text = "40.7128,-74.0060,51.5074,-0.1278\n-90, -180, 90, 180"
    pairs, invalid = _parse_distance_pairs(text)
    assert len(pairs) == 2
    assert len(invalid) == 0
    assert pairs[0] == (40.7128, -74.0060, 51.5074, -0.1278)

    # Invalid pairs
    text_invalid = "10,20\nfoo,bar,baz,qux\n200,10,20,30\n10,20,300,40"
    pairs, invalid = _parse_distance_pairs(text_invalid)
    assert len(pairs) == 0
    assert len(invalid) == 4
    assert invalid[0][1] == "Expected lat1, lon1, lat2, lon2"
    assert invalid[1][1] == "Not a number"
    assert invalid[2][1] == "Point A out of range (-90 <= lat <= 90, -180 <= lon <= 180)"
    assert invalid[3][1] == "Point B out of range (-90 <= lat <= 90, -180 <= lon <= 180)"

def test_calculate_distance():
    text = "40.7128,-74.0060,51.5074,-0.1278"
    result = calculate_distance(text)
    assert "Point A Lat" in result
    assert "Distance (km)" in result

    text_invalid = "invalid_data"
    result_invalid = calculate_distance(text_invalid)
    assert "No valid coordinate pairs provided" in result_invalid
