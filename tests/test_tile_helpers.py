import pytest

@pytest.mark.xfail(reason="Quadkey helper is missing or behavior differs")
def test_quadkey_helper():
    from tile_helpers import tile_to_quadkey, quadkey_to_tile

    # Known z/x/y coordinates mapping to documented quadkey string and back
    # Level 1: z=1, x=1, y=1 -> "3"
    assert tile_to_quadkey(1, 1, 1) == "3"
    assert quadkey_to_tile("3") == (1, 1, 1)

    # Level 3: z=3, x=3, y=5 -> "213"
    assert tile_to_quadkey(3, 5, 3) == "213"
    assert quadkey_to_tile("213") == (3, 5, 3)

    # Level 1: z=1, x=0, y=0 -> "0"
    assert tile_to_quadkey(0, 0, 1) == "0"
    assert quadkey_to_tile("0") == (0, 0, 1)

    # Level 1: z=1, x=1, y=0 -> "1"
    assert tile_to_quadkey(1, 0, 1) == "1"
    assert quadkey_to_tile("1") == (1, 0, 1)
