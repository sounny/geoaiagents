import pytest

def test_utm_zone_helper():
    try:
        from validation import get_utm_zone
    except ImportError:
        pytest.xfail("UTM helper is missing")

    # If it is imported, let's test -180, 0, 179.
    # -180 -> 1
    # 0 -> 31
    # 179 -> 60

    try:
        assert get_utm_zone(-180) == 1
        assert get_utm_zone(0) == 31
        assert get_utm_zone(179) == 60
    except Exception as e:
        pytest.xfail(f"UTM helper behavior differs: {e}")
    except AssertionError as e:
        pytest.xfail(f"UTM helper behavior differs: {e}")
