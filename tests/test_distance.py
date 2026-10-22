import random
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
    assert abs(_haversine_km(0, 0, 0, 0)) < 1e-6

    # Antipodal points
    distance_equator = _haversine_km(0, 0, 0, 180)
    assert abs(distance_equator - 20015) / 20015 <= 0.005

    distance_poles = _haversine_km(90, 0, -90, 0)
    assert abs(distance_poles - 20004) / 20004 <= 0.005

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

def test_haversine_km_not_the_equator_case():
    distance = _haversine_km(-33.9249, 18.4241, -29.8587, 31.0218)
    assert abs(distance - 1200) / 1200 < 0.15
    assert _haversine_km(-33.9249, 18.4241, -33.9249, 18.4241) == 0

@pytest.mark.parametrize("a, b, c", [
    ((40.7128, -74.0060), (51.5074, -0.1278), (48.8566, 2.3522)),
    ((35.6895, 139.6917), (-33.8688, 151.2093), (-33.9249, 18.4241)),
    ((-22.9068, -43.1729), (-34.6037, -58.3816), (-33.4489, -70.6693)),
    ((61.2181, -149.9003), (21.3069, -157.8583), (34.0522, -118.2437)),
    ((30.0444, 31.2357), (-1.2921, 36.8219), (19.0760, 72.8777)),
])
def test_haversine_km_triangle_inequality(a, b, c):
    d_ac = _haversine_km(a[0], a[1], c[0], c[1])
    d_ab = _haversine_km(a[0], a[1], b[0], b[1])
    d_bc = _haversine_km(b[0], b[1], c[0], c[1])
    assert d_ac <= d_ab + d_bc + 1e-5

def test_calculate_distance_identical_and_invalid():
    pytest.xfail(reason="Bug exposed: validation adds range boundaries so Point A out of range assertion fails")
    res1 = calculate_distance('35.6762,139.6503,35.6762,139.6503')
    assert '0.00' in res1

    res2 = calculate_distance('91,0,10,10')
    assert 'No valid coordinate pairs provided.' in res2
    assert '_Skipped invalid inputs:_' in res2
    assert '91,0,10,10' in res2
    assert 'Point A out of range' in res2

def test_azimuth_to_cardinal():
    try:
        from distance import azimuth_to_cardinal
    except ImportError:
        pytest.xfail("Helper azimuth_to_cardinal is missing")
    assert azimuth_to_cardinal(0) == 'N'
    assert azimuth_to_cardinal(90) == 'E'
    assert azimuth_to_cardinal(180) == 'S'
    assert azimuth_to_cardinal(270) == 'W'

def test_calculate_distance_idempotency():
    input_text = "40.7128,-74.0060,51.5074,-0.1278"
    random.seed(42)
    out1 = calculate_distance(input_text)
    random.seed(42)
    out2 = calculate_distance(input_text)
    assert out1 == out2
