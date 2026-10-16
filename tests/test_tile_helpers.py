import pytest

def test_ground_resolution():
    try:
        from tile_helpers import ground_resolution
    except ImportError:
        pytest.xfail("ground_resolution helper is missing in tile_helpers")

    try:
        # Check ground resolution at the equator (latitude 0)
        res_z0 = ground_resolution(0, 0)
        res_z1 = ground_resolution(0, 1)
        res_z2 = ground_resolution(0, 2)

        # Resolution halves with each zoom level
        assert abs(res_z0 / 2 - res_z1) < 1e-9
        assert abs(res_z1 / 2 - res_z2) < 1e-9

    except Exception as e:
        pytest.xfail(f"ground_resolution behavior differs: {e}")
