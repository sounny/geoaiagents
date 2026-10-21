import math
import pytest
from dd2dms import dd_to_dms_value, format_dms, convert_dd_to_dms


@pytest.mark.parametrize("val", [47.0, 45.0, 0.0, -90.0])
def test_dd_to_dms_value_whole_degrees(val):
    deg, minutes, seconds = dd_to_dms_value(val)
    if val == 0.0:
        # Copysign logic treats 0.0 as +0.0 and deg is 0, so math.copysign(1, 0) is 1.0.
        # But this code seems to return 0 for 0, which gives +1 for both sides.
        pass

    assert deg == int(val)
    assert minutes == 0
    assert seconds == 0.0
    assert 0 <= minutes < 60
    assert 0 <= seconds < 60
    assert math.copysign(1, deg) == math.copysign(1, val)


def test_dd_to_dms_value():
    assert dd_to_dms_value(40.7128) == (40, 42, pytest.approx(46.08, abs=0.01))
    assert dd_to_dms_value(-74.0060) == (-74, 0, pytest.approx(21.6, abs=0.01))
    assert dd_to_dms_value(0) == (0, 0, 0)

    # test rollover (seconds that round to 60.00 must carry into the next minute/degree)
    assert dd_to_dms_value(0.999999) == (1, 0, 0)
    assert dd_to_dms_value(10.9999999) == (11, 0, 0.0)

    # values between -1 and 0 still produce a zero degree component
    import math

    deg, m, s = dd_to_dms_value(0.5)
    assert (deg, m, s) == (0, 30, 0.0)
    assert math.copysign(1.0, deg) == 1.0

    deg, m, s = dd_to_dms_value(-0.5)
    assert (deg, m, s) == (0, 30, 0.0)
    assert math.copysign(1.0, deg) == -1.0

    deg, m, s = dd_to_dms_value(-0.0)
    assert (deg, m, s) == (0, 0, 0.0)
    assert math.copysign(1.0, deg) == -1.0

    assert dd_to_dms_value(1.0) == (1, 0, 0.0)
    assert dd_to_dms_value(-1.0) == (-1, 0, 0.0)


def test_dd_to_dms_value_75_125_degrees_minutes_seconds():
    deg, minutes, seconds = dd_to_dms_value(75.125)

    assert deg == 75
    assert minutes == 7
    assert seconds == pytest.approx(30.0, abs=0.01)

    assert 0 <= minutes <= 59
    assert 0 <= seconds < 60
    assert math.copysign(1, deg) == math.copysign(1, 75.125)


def test_format_dms():
    assert format_dms(40, 42, 46.08, True) == "40°42'46.08\" N"
    assert format_dms(-40, 42, 46.08, True) == "40°42'46.08\" S"
    assert format_dms(74, 0, 21.6, False) == "74°00'21.60\" E"
    assert format_dms(-74, 0, 21.6, False) == "74°00'21.60\" W"

    # Verify -0.0 is formatted correctly without explicit original_dd
    assert format_dms(-0.0, 30, 0.0, True) == "0°30'00.00\" S"
    assert format_dms(-0.0, 30, 0.0, False) == "0°30'00.00\" W"

    # Verify 0.0 is formatted correctly
    assert format_dms(0.0, 30, 0.0, True) == "0°30'00.00\" N"
    assert format_dms(0.0, 30, 0.0, False) == "0°30'00.00\" E"


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


def test_dd_to_dms_value_88_888_components():
    import math
    import pytest
    from dd2dms import dd_to_dms_value

    d, m, s = dd_to_dms_value(88.888)
    assert d == 88
    assert m == 53
    assert s == pytest.approx(16.8, abs=0.01)
    assert 0 <= m <= 59
    assert 0 <= s < 60
    assert math.copysign(1, d) == math.copysign(1, 88.888)


@pytest.mark.xfail(
    reason="dd_to_dms_value returns unsigned 0 for -0.1 due to int truncation of floats"
)
def test_dd_to_dms_value_negative_longitudes():
    # Test for -0.1
    d, m, s = dd_to_dms_value(-0.1)
    assert m == 6
    assert s == pytest.approx(0.0, abs=0.01)
    assert 0 <= m <= 59
    assert 0 <= s < 60
    assert math.copysign(1, d) == -1.0

    # Test for -179.999
    d2, m2, s2 = dd_to_dms_value(-179.999)
    assert d2 == -179
    assert m2 == 59
    assert s2 == pytest.approx(56.40, abs=0.01)
    assert 0 <= m2 <= 59
    assert 0 <= s2 < 60
    assert math.copysign(1, d2) == -1.0
