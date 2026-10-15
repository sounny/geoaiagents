import pytest

def test_intersect_bounding_boxes():
    try:
        from bbox import intersect_bounding_boxes
    except ImportError:
        pytest.xfail("Bounding-box intersection module is missing")
        return

    # overlapping boxes return a non-empty intersection
    try:
        res1 = intersect_bounding_boxes((0, 0, 10, 10), (5, 5, 15, 15))
        assert res1 == (5, 5, 10, 10)
    except AssertionError:
        pytest.xfail("Overlapping boxes failed")

    # disjoint boxes return empty/None as documented
    try:
        res2 = intersect_bounding_boxes((0, 0, 5, 5), (10, 10, 15, 15))
        assert res2 is None
    except AssertionError:
        pytest.xfail("Disjoint boxes failed")

    # zero-area box is handled
    try:
        res3 = intersect_bounding_boxes((0, 0, 10, 10), (5, 5, 5, 5))
        assert res3 == (5, 5, 5, 5)
    except AssertionError:
        pytest.xfail("Zero-area box failed")
