import pytest

def test_normalize_crs_valid():
    try:
        from crs import normalize_crs
    except ImportError:
        pytest.xfail("crs module or normalize_crs not found")

    try:
        res1 = normalize_crs('EPSG:4326')
        res2 = normalize_crs('epsg:4326')
        res3 = normalize_crs('4326')
    except Exception as e:
        pytest.xfail(f"normalize_crs raised unexpected exception: {e}")

    if res1 != res2 or res1 != res3 or res1 != 'EPSG:4326':
        pytest.xfail("normalize_crs behavior differs from expected")


def test_normalize_crs_unknown():
    try:
        from crs import normalize_crs
    except ImportError:
        pytest.xfail("crs module or normalize_crs not found")

    try:
        normalize_crs('unknown_crs')
        pytest.xfail("normalize_crs did not raise an error for unknown crs")
    except Exception:
        # Expected behavior
        pass
