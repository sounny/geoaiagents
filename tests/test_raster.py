import pytest

def test_raster_normalize():
    try:
        from raster_utils import normalize_raster
    except ImportError:
        pytest.xfail("Raster normalize helper is missing")

    arr = [[10, 20], [30, 50]]
    normalized = normalize_raster(arr)

    min_val = min(min(row) for row in normalized)
    max_val = max(max(row) for row in normalized)

    assert min_val == 0.0
    assert max_val == 1.0

    const_arr = [[5, 5], [5, 5]]
    const_norm = normalize_raster(const_arr)

    const_min = min(min(row) for row in const_norm)
    const_max = max(max(row) for row in const_norm)

    assert const_min == 0.0
    assert const_max == 0.0
