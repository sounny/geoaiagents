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

def test_dd_to_dms_rounding_edge_cases():
    # Value that rounds up to 60 seconds (59.996s -> 60.00s -> +1 min)
    # 59m 59.996s -> 3599.996s / 3600 = 0.9999988888888889
    assert dd_to_dms_value(0.9999988888888889) == (1, 0, 0.0)

    # Value just below the rounding boundary (59.994s -> 59.99s)
    # 59m 59.994s -> 3599.994s / 3600 = 0.9999983333333333
    assert dd_to_dms_value(0.9999983333333333) == (0, 59, 59.99)

    # Let's test a value that rolls over minutes but not degrees.
    # 0 deg, 0m, 59.996s = 59.996 / 3600 = 0.016665555555555556
    assert dd_to_dms_value(0.016665555555555556) == (0, 1, 0.0)

    # Let's test a value that rolls over minutes but not degrees, at an arbitrary degree.
    # 12 deg, 30m, 59.996s = (12 * 3600 + 30 * 60 + 59.996) / 3600 = 12.516665555555556
    assert dd_to_dms_value(12.516665555555556) == (12, 31, 0.0)
