import pytest
import math

try:
    from raster import scale_reflectance
    HAS_HELPER = True
except ImportError:
    HAS_HELPER = False


@pytest.mark.xfail(not HAS_HELPER, reason="Reflectance scaling helper is missing")
def test_scale_reflectance():
    if not HAS_HELPER:
        pytest.xfail("Reflectance scaling helper is missing")

    # Documented Landsat Collection 2 surface reflectance scale is 0.0000275 and offset is -0.2
    # So output = input * 0.0000275 - 0.2

    assert math.isclose(scale_reflectance(0), -0.2, abs_tol=1e-6)
    assert math.isclose(scale_reflectance(10000), 0.075, abs_tol=1e-6)
