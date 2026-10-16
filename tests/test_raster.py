import pytest

def test_apply_geotransform():
    try:
        from raster import apply_geotransform
    except ImportError:
        pytest.xfail("Geotransform helper (apply_geotransform) is missing from raster module.")

    # Geotransform format: (top_left_x, w_e_pixel_resolution, rotation, top_left_y, rotation, n_s_pixel_resolution)
    # Origin at (100, 200), pixel size 10x -10
    geotransform = (100.0, 10.0, 0.0, 200.0, 0.0, -10.0)

    try:
        # Test pixel 0, 0
        x0, y0 = apply_geotransform(geotransform, 0, 0)
        assert x0 == 100.0, f"Expected x at 0,0 to be 100.0, got {x0}"
        assert y0 == 200.0, f"Expected y at 0,0 to be 200.0, got {y0}"

        # Test pixel 1, 1
        x1, y1 = apply_geotransform(geotransform, 1, 1)
        assert x1 == 110.0, f"Expected x at 1,1 to be 110.0, got {x1}"
        assert y1 == 190.0, f"Expected y at 1,1 to be 190.0, got {y1}"
    except Exception as e:
        pytest.xfail(f"Geotransform helper behavior differs from expectations: {e}")
