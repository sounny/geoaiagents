import pytest
from distance import _parse_distance_pairs, _haversine_km, calculate_distance, calculate_path_length

def test_parse_distance_pairs():
    text = "0,0,10,10\n91,0,0,0\nabc,123,0,0\n10, 20, 30, 40"
    pairs, invalid = _parse_distance_pairs(text)
    assert pairs == [(0, 0, 10, 10), (10, 20, 30, 40)]
    assert len(invalid) == 2
    assert invalid[0][0] == "91,0,0,0"
    assert invalid[1][0] == "abc,123,0,0"

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

def test_calculate_path_length_empty():
    assert calculate_path_length([]) == 0.0

def test_calculate_path_length_single():
    assert calculate_path_length([(40.7128, -74.0060)]) == 0.0

def test_calculate_path_length_multiple():
    coords = [
        (40.7128, -74.0060),  # NYC
        (51.5074, -0.1278),   # London
        (48.8566, 2.3522)     # Paris
    ]
    # NYC to London is ~5570km, London to Paris is ~343km
    dist = calculate_path_length(coords)
    assert 5800 < dist < 6000
