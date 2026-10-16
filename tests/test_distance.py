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

def test_haversine_km_not_the_equator_case():
    distance = _haversine_km(-33.9249, 18.4241, -29.8587, 31.0218)
    assert abs(distance - 1200) / 1200 < 0.15
    assert _haversine_km(-33.9249, 18.4241, -33.9249, 18.4241) == 0

def test_calculate_distance_identical_and_invalid():
    res1 = calculate_distance('35.6762,139.6503,35.6762,139.6503')
    assert '0.00' in res1

    res2 = calculate_distance('91,0,10,10')
    assert 'No valid coordinate pairs provided.' in res2
    assert '_Skipped invalid inputs:_' in res2
    assert '91,0,10,10' in res2
    assert 'Point A out of range' in res2

def test_google_polyline_helper():
    try:
        from distance import encode_polyline, decode_polyline
    except ImportError:
        pytest.xfail("Google polyline helper (encode_polyline/decode_polyline) is missing.")

    original_points = [(38.5, -120.2), (40.7, -120.95), (43.252, -126.453)]
    encoded = encode_polyline(original_points)
    decoded = decode_polyline(encoded)

    assert len(original_points) == len(decoded)
    for (orig_lat, orig_lon), (dec_lat, dec_lon) in zip(original_points, decoded):
        assert abs(orig_lat - dec_lat) < 1e-5
        assert abs(orig_lon - dec_lon) < 1e-5
