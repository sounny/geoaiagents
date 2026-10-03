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

def test_calculate_distance_conversion():
    text = "48.8566,2.3522,51.5074,-0.1278"
    result = calculate_distance(text)

    # Split the result into lines
    lines = result.strip().split("\n")

    # We expect 3 lines: headers, separator, and 1 data row
    assert len(lines) == 3

    # The third line is the data row
    data_row = lines[2]

    # Split by pipe '|' and clean up spaces
    # The columns are: empty, Point A Lat, Point A Lon, Point B Lat, Point B Lon, Distance (km), Distance (mi), empty
    columns = [col.strip() for col in data_row.split("|")]

    km = float(columns[5])
    mi = float(columns[6])

    # Assert mi is roughly km * 0.621371
    assert abs(mi - km * 0.621371) < 0.02
