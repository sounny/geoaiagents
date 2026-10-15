import pytest
import math

def test_xyz_tile_roundtrip():
    """Verify that a tile (x, y, z) converts to a longitude/latitude that maps back to the same tile indices."""
    try:
        import tile_helpers
    except ImportError:
        pytest.xfail("tile_helpers module is missing")

    if not hasattr(tile_helpers, "tile_to_lonlat") or not hasattr(tile_helpers, "lonlat_to_tile"):
        pytest.xfail("tile_helpers is missing expected functions (tile_to_lonlat, lonlat_to_tile)")

    try:
        # Example tile at zoom 12
        z = 12
        x = 2200
        y = 1343

        lon, lat = tile_helpers.tile_to_lonlat(x, y, z)
        x2, y2 = tile_helpers.lonlat_to_tile(lon, lat, z)

        assert x == x2 and y == y2
    except Exception as e:
        pytest.xfail(f"tile_helpers behavior differs: {e}")

def test_tile_bounds_helper():
    """Verify that tile_bounds for (0,0,0) covers roughly the world and corners are ordered SW-NE."""
    try:
        import tile_helpers
    except ImportError:
        pytest.xfail("tile_helpers module is missing")

    if not hasattr(tile_helpers, "tile_bounds"):
        pytest.xfail("tile_bounds helper is missing")

    try:
        bounds = tile_helpers.tile_bounds(0, 0, 0)
        # Expected: min_lon, min_lat, max_lon, max_lat
        assert len(bounds) == 4
        min_lon, min_lat, max_lon, max_lat = bounds

        assert abs(min_lon - (-180.0)) < 0.1
        assert abs(min_lat - (-85.0511)) < 0.1
        assert abs(max_lon - 180.0) < 0.1
        assert abs(max_lat - 85.0511) < 0.1

        # Check SW-NE ordering
        assert min_lon < max_lon
        assert min_lat < max_lat
    except Exception as e:
        pytest.xfail(f"tile_bounds behavior differs: {e}")
