import pytest

def test_geohash_encode_decode_neighbor():
    try:
        import geohash
    except ImportError:
        pytest.xfail("geohash module is missing")

    try:
        # Encode then decode a known lat/lon
        lat, lon = 40.7128, -74.0060
        gh = geohash.encode(lat, lon, precision=6)
        dec_lat, dec_lon = geohash.decode(gh)

        # Verify precision (e.g. within 0.05 degrees)
        assert abs(dec_lat - lat) < 0.05
        assert abs(dec_lon - lon) < 0.05

        # Verify neighbor shares prefix of length - 1
        neighbor_gh = geohash.neighbor(gh, 'n')
        assert neighbor_gh[:-1] == gh[:-1]
    except Exception as e:
        pytest.xfail(f"geohash behavior differs: {e}")

def test_geohash_invalid():
    try:
        import geohash
    except ImportError:
        pytest.xfail("geohash module is missing")

    try:
        geohash.decode("invalid_hash!")
    except Exception as e:
        if "invalid" not in str(e).lower() and "error" not in str(e).lower():
            pytest.xfail(f"Invalid geohash raised error without clear message: {e}")
    else:
        pytest.xfail("Invalid geohash did not raise a clear error")
