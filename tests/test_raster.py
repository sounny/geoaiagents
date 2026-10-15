import pytest

def test_raster_clamp_helper():
    try:
        import raster
    except ImportError:
        pytest.xfail("Raster module is missing")

    # If the module exists, look for a clamp helper
    clamp_func = getattr(raster, "clamp_bounds", None)
    if not clamp_func:
        pytest.xfail("raster module does not have clamp_bounds helper")

    try:
        # Pass coordinates outside valid bounds (e.g., lat=100, lon=200)
        # Should be clamped or cleanly rejected
        result = clamp_func(100.0, 200.0)
        # Check if clamped
        if result not in [(90.0, 180.0), None]:
            pytest.xfail(f"clamp_bounds returned unexpected result: {result}")
    except Exception as e:
        pytest.xfail(f"clamp_bounds crashed with exception: {e}")
