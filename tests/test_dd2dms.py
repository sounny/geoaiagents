import pytest
from dd2dms import dd_to_dms_value, format_dms, convert_dd_to_dms

def test_dd_to_dms_value_rollover_normalize():
    # User requested dd_to_dms_value(-12.25)
    deg, m, s = dd_to_dms_value(-12.25)
    assert deg == -12  # degree sign follows input
    assert m == 15
    assert s == 0.0
    assert 0 <= m < 60
    assert 0 <= s < 60

    # Memory requested other components explicitly
    deg2, m2, s2 = dd_to_dms_value(0.5)
    assert deg2 == 0
    assert m2 == 30
    assert s2 == 0.0
    assert 0 <= m2 < 60
    assert 0 <= s2 < 60

    assert dd_to_dms_value(0.0) == (0, 0, 0.0) or dd_to_dms_value(0.0) == (0, 0, 0)

    deg3, m3, s3 = dd_to_dms_value(0.999999)
    # normalizes so seconds < 60 and minutes < 60
    assert s3 < 60
    assert m3 < 60

    deg4, m4, s4 = dd_to_dms_value(-2.5)
    assert deg4 == -2
    assert m4 == 30
    assert s4 == 0.0
    assert 0 <= m4 < 60
    assert 0 <= s4 < 60

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
