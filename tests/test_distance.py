import pytest
from distance import _parse_distance_pairs, _haversine_km, calculate_distance

def test_parse_distance_pairs():
    text = "0,0,10,10\n91,0,0,0\nabc,123,0,0\n10, 20, 30, 40"
    pairs, invalid = _parse_distance_pairs(text)
    assert pairs == [(0, 0, 10, 10), (10, 20, 30, 40)]
    assert len(invalid) == 2
    assert invalid[0][0] == "91,0,0,0"
    assert invalid[1][0] == "abc,123,0,0"

def test_parse_distance_pairs_tab_separated():
    text = '48.8566\t2.3522\t51.5074\t-0.1278'
    pairs, invalid = _parse_distance_pairs(text)
    assert len(pairs) == 1
    assert len(invalid) == 0
    p = pairs[0]
    assert abs(p[0] - 48.8566) < 1e-6
    assert abs(p[1] - 2.3522) < 1e-6
    assert abs(p[2] - 51.5074) < 1e-6
    assert abs(p[3] - (-0.1278)) < 1e-6

def test_parse_distance_pairs_empty():
    pairs, invalid = _parse_distance_pairs('')
    assert pairs == []

def test_parse_distance_pairs_point_a_out_of_range():
    pairs, invalid = _parse_distance_pairs('91.0,0.0,0.0,0.0')
    assert pairs == []
    assert len(invalid) == 1
    assert "Point A out of range" in invalid[0][1]

def test_parse_distance_pairs_point_b_out_of_range():
    pairs, invalid = _parse_distance_pairs('0.0,0.0,91.0,0.0')
    assert pairs == []
    assert len(invalid) == 1
    assert "Point B out of range" in invalid[0][1]

def test_parse_distance_pairs_short_line():
    pairs, invalid = _parse_distance_pairs('19,14')
    assert pairs == []
    assert len(invalid) == 1
    assert "Expected lat1" in invalid[0][1]

def test_parse_distance_pairs_all_zero():
    pairs, invalid = _parse_distance_pairs('0.0,0.0,0.0,0.0')
    assert pairs == [(0.0, 0.0, 0.0, 0.0)]
    assert invalid == []

def test_haversine_km():
    # New York to London
    distance = _haversine_km(40.7128, -74.0060, 51.5074, -0.1278)
    assert 5500 < distance < 5600

def test_calculate_distance():
    text = "40.7128,-74.0060,51.5074,-0.1278"
    result = calculate_distance(text)
    assert "40.7128" in result
    assert "51.5074" in result
    assert "Distance (km)" in result

def test_calculate_distance_malformed():
    result = calculate_distance("invalid\n10,20,30,400\n10,20,30,foo")
    assert "No valid coordinate pairs provided." in result
    assert "_Skipped invalid inputs:_" in result
    assert "invalid" in result
    assert "Expected lat1, lon1, lat2, lon2" in result
    assert "10,20,30,400" in result
    assert "Point B out of range" in result
    assert "10,20,30,foo" in result
    assert "Not a number" in result

def test_calculate_distance_empty():
    result = calculate_distance("")
    assert result == "No valid coordinate pairs provided."
