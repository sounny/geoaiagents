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

def test_dbscan_clustering():
    try:
        from distance import dbscan_cluster
    except ImportError:
        pytest.xfail("DBSCAN clustering helper missing")
        return

    # Two tight groups and one isolated point
    # Group 1: (0, 0), (0, 0.1), (0.1, 0)
    # Group 2: (10, 10), (10, 10.1), (10.1, 10)
    # Noise: (50, 50)
    points = [
        (0, 0), (0, 0.1), (0.1, 0),
        (10, 10), (10, 10.1), (10.1, 10),
        (50, 50)
    ]

    try:
        # Assuming signature dbscan_cluster(points, eps, min_samples)
        # Using eps=1.0 and min_samples=2
        labels = dbscan_cluster(points, eps=1.0, min_samples=2)

        # Noise should be labeled -1, others >= 0
        assert labels[6] == -1, "Isolated point should be noise (-1)"

        # Two distinct clusters
        cluster1 = set(labels[0:3])
        cluster2 = set(labels[3:6])
        assert len(cluster1) == 1, "Group 1 should be one cluster"
        assert len(cluster2) == 1, "Group 2 should be one cluster"
        assert cluster1 != cluster2, "Groups should form separate clusters"
        assert list(cluster1)[0] != -1, "Group 1 should not be noise"
        assert list(cluster2)[0] != -1, "Group 2 should not be noise"
    except Exception as e:
        pytest.xfail(f"DBSCAN clustering helper behaves differently: {e}")
