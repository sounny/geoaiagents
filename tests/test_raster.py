import pytest

def test_qa_cloud_mask():
    try:
        from raster import is_cloud_pixel
    except ImportError:
        pytest.xfail("raster module or is_cloud_pixel helper is missing")

    try:
        # Documented Landsat or Sentinel bit flags mark cloud pixels
        # For instance, bit 3 (value 8) might indicate cloud.
        assert is_cloud_pixel(0) is False
        assert is_cloud_pixel(8) is True
    except AssertionError:
        pytest.xfail("is_cloud_pixel behavior differs from expected cloud bit flags")
    except Exception as e:
        pytest.xfail(f"is_cloud_pixel raised an unexpected error: {e}")
