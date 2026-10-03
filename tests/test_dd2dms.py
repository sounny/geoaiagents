import pytest
from dd2dms import dd_to_dms_value, format_dms, convert_dd_to_dms

import math

def test_dd_to_dms_value_33_333():
    deg, minutes, seconds = dd_to_dms_value(33.333)
    assert (deg, minutes, seconds) == (33, 19, pytest.approx(58.8, abs=0.01))
    assert 0 <= minutes <= 59
    assert 0 <= seconds < 60
    assert math.copysign(1, deg) == math.copysign(1, 33.333)

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

def test_dd_to_dms_value_51_25_components():
    import math
    import pytest
    from dd2dms import dd_to_dms_value

    d, m, s = dd_to_dms_value(51.25)

    assert d == 51
    assert m == 15
    assert s == pytest.approx(0.0, abs=0.01)
    assert 0 <= m <= 59
    assert 0 <= s < 60
    assert math.copysign(1, d) == math.copysign(1, 51.25)
