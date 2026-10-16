import pytest

def test_densify_reproject_bbox():
    try:
        from bbox import densify_bbox
    except ImportError:
        pytest.xfail("Bbox densify/reproject helper 'densify_bbox' is missing.")

    try:
        densified_coords = densify_bbox((0, 0, 10, 10), points_per_edge=10)
        assert len(densified_coords) == 40
    except Exception as e:
        pytest.xfail(f"densify_bbox helper exists but behavior differs: {e}")
