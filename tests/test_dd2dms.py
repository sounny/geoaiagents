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

def test_convert_dd_to_dms_invalid_only():
    res = convert_dd_to_dms("not-a-pair\n91,0")
    lines = res.splitlines()
    assert len(lines) == 5
    assert lines[0] == "| Latitude (DD) | Longitude (DD) | Latitude (DMS) | Longitude (DMS) |"
    assert lines[1] == "|--------------:|---------------:|---------------|---------------|"
    assert lines[2] == "_Skipped invalid inputs:_"
    assert lines[3] == "- `not-a-pair` (Missing latitude/longitude pair)"
    assert lines[4] == "- `91,0` (Out of range (-90 <= lat <= 90, -180 <= lon <= 180))"
