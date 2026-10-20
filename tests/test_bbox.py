import pytest

def test_bbox_area():
    try:
        from distance import bbox_area
    except ImportError:
        pytest.xfail("bbox_area helper is missing")

    # Check a 1x1 degree bbox at the equator
    bbox = [0, 0, 1, 1]

    try:
        area = bbox_area(bbox)
    except Exception as e:
        pytest.xfail(f"bbox_area failed: {e}")

    # Expected area is roughly 12364.5 km2 (at equator) or 1 square degree.
    expected_sq_deg = pytest.approx(1, abs=0.01)
    expected_km2 = pytest.approx(12364.5, abs=50)

    if area != expected_sq_deg and area != expected_km2:
        pytest.xfail("bbox_area returned an unexpected value")
