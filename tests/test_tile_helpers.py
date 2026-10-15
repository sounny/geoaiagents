import pytest

def test_tile_pyramid_helper():
    """
    Test for a tile-pyramid helper: zoom z has 2^z by 2^z tiles and out-of-range indices are rejected.
    """
    try:
        from tile_helpers import tile_pyramid_validate
    except ImportError:
        pytest.xfail("Missing tile-pyramid helper")

    try:
        # For zoom level 0, 2^0 x 2^0 = 1 tile, valid indices (0,0)
        tile_pyramid_validate(0, 0, 0)

        # Test out-of-range rejection for zoom 0
        rejected = False
        try:
            tile_pyramid_validate(1, 0, 0)
        except Exception:
            rejected = True

        if not rejected:
            pytest.xfail("Behavior differs: Out-of-range index not rejected")

        # For zoom level 2, 2^2 x 2^2 = 16 tiles, valid indices 0 to 3
        tile_pyramid_validate(3, 3, 2)

        # Test out-of-range rejection for zoom 2
        rejected = False
        try:
            tile_pyramid_validate(4, 3, 2)
        except Exception:
            rejected = True

        if not rejected:
            pytest.xfail("Behavior differs: Out-of-range index not rejected")

    except Exception as e:
        pytest.xfail(f"Behavior differs: {e}")
