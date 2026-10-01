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

def test_format_dms_hemisphere_specific_2_5_and_zero():
    deg, minutes, seconds = dd_to_dms_value(2.5)

    # original_dd=2.5, is_lat=False -> 'E'
    res_e = format_dms(deg, minutes, seconds, is_lat=False, original_dd=2.5)
    assert 'E' in res_e

    # original_dd=-2.5, is_lat=False -> 'W'
    res_w = format_dms(deg, minutes, seconds, is_lat=False, original_dd=-2.5)
    assert 'W' in res_w

    # original_dd=0, is_lat=True -> 'N' or 'S'
    res_zero_lat = format_dms(deg, minutes, seconds, is_lat=True, original_dd=0.0)
    assert 'N' in res_zero_lat or 'S' in res_zero_lat

def test_dd_to_dms_value_zero_and_negative_2_5():
    deg, minutes, seconds = dd_to_dms_value(0.0)
    assert deg == 0
    assert minutes == 0
    assert pytest.approx(0.0, abs=0.01) == seconds

    deg, minutes, seconds = dd_to_dms_value(-2.5)
    assert abs(deg) == 2
    assert minutes == 30
    assert pytest.approx(0.0, abs=0.01) == seconds

def test_dd_to_dms_value_components():
    deg, minutes, seconds = dd_to_dms_value(48.8566)
    assert deg == 48
    assert minutes == 51
    assert pytest.approx(23.76, abs=0.05) == seconds

    deg, minutes, seconds = dd_to_dms_value(-0.1278)
    assert abs(deg) == 0
    assert minutes >= 7
    assert pytest.approx(40.08, abs=0.05) == seconds

def test_convert_dd_to_dms_invalid_inputs():
    res = convert_dd_to_dms("91,0")
    assert "| Latitude (DD) | Longitude (DD) | Latitude (DMS) | Longitude (DMS) |" in res
    assert res.count("\n|") >= 1
    assert "_Skipped invalid inputs:_" in res
    assert "`91,0`" in res

def test_convert_dd_to_dms_empty_string():
    res = convert_dd_to_dms("")
    assert "| Latitude (DD) | Longitude (DD) | Latitude (DMS) | Longitude (DMS) |" in res
    assert "|--------------:|---------------:|---------------|---------------|" in res
    assert res.count("\n|") == 1
