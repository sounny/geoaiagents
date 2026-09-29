import pytest
from dd2dms import dd_to_dms_value, format_dms, convert_dd_to_dms

def test_dd_to_dms_value():
    assert dd_to_dms_value(40.7128) == (40, 42, pytest.approx(46.08, abs=0.01))
    assert dd_to_dms_value(-74.0060) == (-74, 0, pytest.approx(21.6, abs=0.01))
    assert dd_to_dms_value(0) == (0, 0, 0)
    # test rollover (seconds that round to 60.00 must carry into the next minute/degree)
    assert dd_to_dms_value(0.999999) == (1, 0, 0)
    # values between -1 and 0 still produce a zero degree component
    assert dd_to_dms_value(0.5) == (0, 30, 0.0)
    assert dd_to_dms_value(-0.5) == (0, 30, 0.0)
    assert dd_to_dms_value(1.0) == (1, 0, 0.0)
    assert dd_to_dms_value(-1.0) == (-1, 0, 0.0)

def test_format_dms():
    assert format_dms(40, 42, 46.08, True) == "40°42'46.08\" N"
    assert format_dms(-40, 42, 46.08, True) == "40°42'46.08\" S"
    assert format_dms(74, 0, 21.6, False) == "74°00'21.60\" E"
    assert format_dms(-74, 0, 21.6, False) == "74°00'21.60\" W"

def test_convert_dd_to_dms():
    text = "40.7128,-74.0060"
    result = convert_dd_to_dms(text)
    assert "40.7128" in result
    assert "-74.0060" in result
    assert "40°42'46.08\" N" in result
    assert "74°00'21.60\" W" in result

def test_convert_dd_to_dms_near_zero_direction():
    # Degrees between -1 and 0 must keep S/W (the degree component truncates to 0).
    res = convert_dd_to_dms("-0.5, -0.5\n0.5, 0.5")
    assert "0°30'00.00\" S" in res
    assert "0°30'00.00\" W" in res
    assert "0°30'00.00\" N" in res
    assert "0°30'00.00\" E" in res

def test_format_dms_explicit():
    # positive lat → N
    assert format_dms(45, 30, 15.123, is_lat=True, original_dd=45.5) == "45°30'15.12\" N"
    # negative lat → S
    assert format_dms(-45, 30, 15.123, is_lat=True, original_dd=-45.5) == "45°30'15.12\" S"
    # positive lon → E
    assert format_dms(45, 30, 15.123, is_lat=False, original_dd=45.5) == "45°30'15.12\" E"
    # negative lon → W
    assert format_dms(-45, 30, 15.123, is_lat=False, original_dd=-45.5) == "45°30'15.12\" W"
    # seconds formatted to exactly two decimals (rounding down)
    assert format_dms(10, 20, 30.111, is_lat=True, original_dd=10.0) == "10°20'30.11\" N"
    # seconds formatted to exactly two decimals (rounding up)
    assert format_dms(10, 20, 30.116, is_lat=True, original_dd=10.0) == "10°20'30.12\" N"
    # seconds formatted with zero padding
    assert format_dms(10, 20, 5.1, is_lat=True, original_dd=10.0) == "10°20'05.10\" N"
