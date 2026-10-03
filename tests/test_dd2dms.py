import pytest
from dd2dms import dd_to_dms_value, format_dms, convert_dd_to_dms

def test_dd_to_dms_value_rollover_normalize():
    assert dd_to_dms_value(40.7128) == (40, 42, pytest.approx(46.08, abs=0.01))
    assert dd_to_dms_value(-74.0060) == (-74, 0, pytest.approx(21.6, abs=0.01))

    # User and memory requested asserts
    # 0.0 limit
    assert dd_to_dms_value(0.0) in [(0, 0, 0), (0, 0, 0.0)]

    # 0.999999 rollover normalizes so seconds < 60 and minutes < 60
    assert dd_to_dms_value(0.999999) == (1, 0, 0.0)

    # 0.5 degrees, minutes, seconds valid limits
    d, m, s = dd_to_dms_value(0.5)
    assert d == 0
    assert 0 <= m <= 59
    assert 0 <= s < 60
    assert (d, m, s) == (0, 30, 0.0)

    # -2.5 negative degrees component and positive minutes/seconds
    d, m, s = dd_to_dms_value(-2.5)
    assert d == -2
    assert 0 <= m <= 59
    assert 0 <= s < 60
    assert (d, m, s) == (-2, 30, 0.0)

    # 66.5 user requested: minutes 0-59, seconds >= 0 and < 60, degree sign follows the input
    d, m, s = dd_to_dms_value(66.5)
    assert d == 66
    assert 0 <= m <= 59
    assert 0 <= s < 60
    assert (d, m, s) == (66, 30, 0.0)

    assert dd_to_dms_value(-0.5) == (0, 30, 0.0)
    assert dd_to_dms_value(1.0) == (1, 0, 0.0)
    assert dd_to_dms_value(-1.0) == (-1, 0, 0.0)

def test_format_dms():
    assert format_dms(40, 42, 46.08, True) == "40°42'46.08\" N"
    assert format_dms(-40, 42, 46.08, True) == "40°42'46.08\" S"
    assert format_dms(74, 0, 21.6, False) == "74°00'21.60\" E"
    assert format_dms(-74, 0, 21.6, False) == "74°00'21.60\" W"

def test_convert_dd_to_dms_western_W():
    text = "40.7128,-74.0060"
    result = convert_dd_to_dms(text)
    assert "40.7128" in result
    assert "-74.0060" in result
    assert "40°42'46.08\" N" in result
    assert "74°00'21.60\" W" in result

    res1 = convert_dd_to_dms("34.05,-118.25")
    assert "W" in res1
    assert "N" in res1
    assert "Latitude" in res1
    assert "Longitude" in res1

    res2 = convert_dd_to_dms("-33.9,151.2")
    assert "S" in res2
    assert "E" in res2

def test_convert_dd_to_dms_valid_and_empty():
    res_valid = convert_dd_to_dms("48.8566,2.3522")
    assert "N" in res_valid
    assert "E" in res_valid
    assert "Latitude" in res_valid
    assert "Longitude" in res_valid

    res_empty = convert_dd_to_dms("")
    assert "Latitude" in res_empty
    assert "Longitude" in res_empty
    assert " N" not in res_empty
    assert " S" not in res_empty
    assert " E" not in res_empty
    assert " W" not in res_empty

def test_convert_dd_to_dms_near_zero_direction():
    # Degrees between -1 and 0 must keep S/W (the degree component truncates to 0).
    res = convert_dd_to_dms("-0.5, -0.5\n0.5, 0.5")
    assert "0°30'00.00\" S" in res
    assert "0°30'00.00\" W" in res
    assert "0°30'00.00\" N" in res
    assert "0°30'00.00\" E" in res
