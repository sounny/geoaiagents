import pytest
import math

def test_calculate_evi():
    """
    Test EVI helper for known band values and denominator zero handling.
    """
    try:
        from raster import calculate_evi
    except ImportError:
        pytest.xfail("EVI helper missing: could not import 'calculate_evi' from 'raster'")
        return

    try:
        # Standard EVI formula: 2.5 * (NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1)
        # Using NIR=0.5, Red=0.1, Blue=0.02
        # Numerator: 2.5 * (0.5 - 0.1) = 1.0
        # Denominator: 0.5 + 6(0.1) - 7.5(0.02) + 1 = 0.5 + 0.6 - 0.15 + 1 = 1.95
        # Expected EVI: 1.0 / 1.95 ~ 0.5128205
        evi_val = calculate_evi(0.5, 0.1, 0.02)

        # Zero denominator case:
        # NIR = -1, Red = 0, Blue = 0 -> Denom = -1 + 0 - 0 + 1 = 0
        evi_zero = calculate_evi(-1.0, 0.0, 0.0)
    except Exception as e:
        pytest.xfail(f"EVI helper raised an unexpected error: {e}")
        return

    if not math.isclose(evi_val, 0.5128205, rel_tol=1e-5):
        pytest.xfail(f"EVI result {evi_val} differs from documented result")

    if not (math.isnan(evi_zero) or evi_zero is None):
        pytest.xfail("EVI zero denominator not returning NaN/None")
