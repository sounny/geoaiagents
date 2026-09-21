import pytest
import math
from distance import _parse_distance_pairs, _haversine_km

def test_parse_distance_pairs():
    text = "40.7128,-74.0060,34.0522,-118.2437"
    pairs, invalid = _parse_distance_pairs(text)
    assert len(pairs) == 1
    assert pairs[0] == (40.7128, -74.0060, 34.0522, -118.2437)
    assert len(invalid) == 0

    text_invalid = "40.7128,-74.0060\n91,0,0,0\n0,0,91,0\nbad,data,here,too"
    pairs, invalid = _parse_distance_pairs(text_invalid)
    assert len(pairs) == 0
    assert len(invalid) == 4
    assert "Expected lat1, lon1, lat2, lon2" in invalid[0][1]
    assert "Point A out of range" in invalid[1][1]
    assert "Point B out of range" in invalid[2][1]
    assert "Not a number" in invalid[3][1]

def test_haversine_km():
    lat1, lon1 = 40.7128, -74.0060
    lat2, lon2 = 34.0522, -118.2437
    dist = _haversine_km(lat1, lon1, lat2, lon2)
    # distance is roughly 3936 km
    assert 3900 < dist < 4000

    # distance to self is 0
    assert _haversine_km(0, 0, 0, 0) == 0
