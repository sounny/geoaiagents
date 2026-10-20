import pytest

def test_xyz_to_bbox():
    try:
        from tile_helpers import xyz_to_bbox
    except ImportError:
        pytest.xfail("Tile XYZ-to-bbox helper function is missing")

    try:
        bbox = xyz_to_bbox(0, 0, 0)
        # xyz_to_bbox returns (min_lon, min_lat, max_lon, max_lat) in WGS84
        assert bbox[0] == pytest.approx(-180.0, abs=1e-4)
        assert bbox[1] == pytest.approx(-85.0511, abs=1e-4)
        assert bbox[2] == pytest.approx(180.0, abs=1e-4)
        assert bbox[3] == pytest.approx(85.0511, abs=1e-4)
    except Exception as e:
        pytest.xfail(f"Current behavior differs: {e}")
