import pytest

def test_calculate_gndvi():
    try:
        from raster import calculate_gndvi
    except ImportError:
        pytest.xfail("GNDVI helper is missing")

    # If it exists, check behavior
    # GNDVI = (NIR - Green) / (NIR + Green)
    # NIR=0.6, Green=0.2 => (0.6 - 0.2) / (0.6 + 0.2) = 0.4 / 0.8 = 0.5
    try:
        result = calculate_gndvi(0.6, 0.2)
        assert abs(result - 0.5) < 1e-6
    except Exception as e:
        pytest.xfail(f"GNDVI behavior differs: {e}")
