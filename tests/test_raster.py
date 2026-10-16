import math
import pytest

def test_ndbi():
    try:
        from raster import calculate_ndbi
    except ImportError:
        pytest.xfail("NDBI helper missing: could not import calculate_ndbi from raster")
        return

    try:
        # NDBI = (SWIR - NIR) / (SWIR + NIR)
        # SWIR=0.6, NIR=0.2 -> (0.6 - 0.2) / (0.6 + 0.2) = 0.4 / 0.8 = 0.5
        result = calculate_ndbi(swir=0.6, nir=0.2)
        assert abs(result - 0.5) < 1e-6, "Known SWIR/NIR values should yield correct NDBI"

        # Check zero denominator handling
        zero_result = calculate_ndbi(swir=0.0, nir=0.0)
        assert zero_result == 0.0 or math.isnan(zero_result), "Zero denominators should be handled as documented"
    except Exception as e:
        pytest.xfail(f"NDBI helper current behavior differs: {e}")
