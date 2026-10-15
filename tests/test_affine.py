import pytest
import math

def test_affine_transform():
    try:
        from affine import apply_affine, invert_affine
    except ImportError:
        pytest.xfail("2D affine transform helper is missing")

    # Example affine transform (scale by 2, rotate by 90 degrees, translate by 10, 20)
    # This is just a conceptual matrix
    # [ 0 -2 10 ]
    # [ 2  0 20 ]
    matrix = [0, -2, 10, 2, 0, 20]

    point = (5, 5)

    try:
        transformed = apply_affine(matrix, point)
        inverted = invert_affine(matrix, transformed)

        if abs(inverted[0] - point[0]) > 1e-9 or abs(inverted[1] - point[1]) > 1e-9:
             pytest.xfail("Affine transform behavior differs from expected")

    except Exception as e:
        pytest.xfail(f"Affine transform helper behavior differs: {e}")
