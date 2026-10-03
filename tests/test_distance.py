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

def test_calculate_distance_multiple_pairs_positive_km():
    result = calculate_distance('48.8566,2.3522,51.5074,-0.1278;40.7128,-74.0060,34.0522,-118.2437')
    assert "Distance (km)" in result
    lines = result.strip().split('\n')
    data_lines = [l for l in lines if l.startswith('|') and 'Point A' not in l and '---' not in l]
    assert len(data_lines) >= 2
    for row in data_lines:
        parts = [p.strip() for p in row.split('|') if p.strip()]
        km_val = float(parts[4])
        assert km_val > 0.0


def test_parse_distance_pairs_tab_and_empty():
    pairs, invalid = _parse_distance_pairs('48.8566\t2.3522\t51.5074\t-0.1278')
    assert len(pairs) == 1
    assert pairs[0] == pytest.approx((48.8566, 2.3522, 51.5074, -0.1278))
    assert invalid == []
    pairs_empty, invalid_empty = _parse_distance_pairs('')
    assert pairs_empty == []

def test_parse_distance_pairs_point_b_out_of_range_and_zeros():
    pairs, invalid = _parse_distance_pairs('0.0,0.0,91.0,0.0')
    assert pairs == []
    assert any("Point B out of range" in reason for _, reason in invalid)

    pairs_zero, invalid_zero = _parse_distance_pairs('0.0,0.0,0.0,0.0')
    assert len(pairs_zero) == 1
    assert pairs_zero[0] == (0.0, 0.0, 0.0, 0.0)

def test_calculate_distance_identical_and_empty_inputs():
    result = calculate_distance('10,20,10,20')
    assert "Distance (km)" in result
    assert "0.00" in result # since both km and mi would be 0.00

    result_empty = calculate_distance('')
    assert result_empty.startswith('No valid coordinate pairs provided.')

def test_haversine_km_antipodal_and_identical():
    distance_antipodal = _haversine_km(0, 0, 0, 180)
    assert abs(distance_antipodal - 20015.0) <= 50.0

    distance_identical = _haversine_km(10, 20, 10, 20)
    assert distance_identical == 0.0


def test_calculate_distance_mi_km_conversion():
    # mi=km*0.621371 relationship check
    result = calculate_distance('48.8566,2.3522,51.5074,-0.1278')
    lines = result.strip().split('\n')
    data_lines = [l for l in lines if l.startswith('|') and 'Point A' not in l and '---' not in l]
    parts = [p.strip() for p in data_lines[0].split('|') if p.strip()]
    km_val = float(parts[4])
    mi_val = float(parts[5])
    assert pytest.approx(mi_val, rel=1e-3) == km_val * 0.621371
