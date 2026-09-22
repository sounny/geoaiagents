import pytest
from dd2dms import dd_to_dms_value, format_dms, convert_dd_to_dms

def test_dd_to_dms_value():
    assert dd_to_dms_value(40.7128) == pytest.approx((40, 42, 46.08))
    assert dd_to_dms_value(-74.0060) == pytest.approx((-74, 0, 21.6))

    # testing rollover
    assert dd_to_dms_value(1.0 + 59.9999/3600) == pytest.approx((1, 1, 0.0))

def test_format_dms():
    assert format_dms(40, 42, 46.08, True) == "40°42'46.08\" N"
    assert format_dms(-74, 0, 21.6, False) == "74°00'21.60\" W"

def test_convert_dd_to_dms():
    res = convert_dd_to_dms("40.7128,-74.0060")
    assert "Latitude (DMS)" in res
    assert "40°42'46.08\" N" in res
    assert "74°00'21.60\" W" in res
