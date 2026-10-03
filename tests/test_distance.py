import pytest
from distance import _parse_distance_pairs, _haversine_km, calculate_distance

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

def test_calculate_distance_paris_london():
    text = "48.8566,2.3522,51.5074,-0.1278"
    result = calculate_distance(text)

    assert "Point A Lat" in result
    assert "Distance (km)" in result
    assert "Distance (mi)" in result

    lines = result.strip().split("\n")
    assert len(lines) == 3, "Expected exactly one data row plus header and separator"

    # Extract the distance in km from the data row
    data_row = lines[2]
    columns = [col.strip() for col in data_row.split("|")]

    # columns[5] should be Distance (km) due to:
    # | Point A Lat | Point A Lon | Point B Lat | Point B Lon | Distance (km) | Distance (mi) |
    # 0 | 1 | 2 | 3 | 4 | 5 | 6 |

    distance_str = columns[5]
    distance = float(distance_str)
    assert distance > 0.0
