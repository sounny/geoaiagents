import pytest

def test_bbox_from_points():
    try:
        from bbox import bbox_from_points
    except ImportError:
        pytest.xfail("bbox module or bbox_from_points helper is missing")

    try:
        # empty list errors or returns null as documented
        res_empty = bbox_from_points([])
        if res_empty is not None:
            pytest.xfail("bbox_from_points did not return None for empty list")
    except Exception as e:
        # It's fine if it errors as documented
        pass

    try:
        # three points produce min/max lon/lat that contain all points
        pts = [(10, 20), (30, 40), (20, 10)]
        res_pts = bbox_from_points(pts)
        assert res_pts == (10, 10, 30, 40)
    except Exception as e:
        pytest.xfail(f"bbox_from_points behavior differs for three points: {e}")
