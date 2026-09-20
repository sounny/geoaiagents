import pytest
from dd2dms import dd_to_dms_value, format_dms, convert_dd_to_dms

def test_dd_to_dms_value():
    # Positive DD
    assert dd_to_dms_value(45.5) == (45, 30, 0.0)

    # Negative DD
    assert dd_to_dms_value(-122.6) == (-122, 36, 0.0)

    # Small value
    result = dd_to_dms_value(0.0001)
    assert result[0] == 0
    assert result[1] == 0
    assert round(result[2], 2) == 0.36

    # Edge case: roll-over at seconds >= 59.9995
    # Let's find a DD that gives 59.9999 seconds
    # e.g., 0 degrees, 0 minutes, 59.9999 seconds
    # total seconds = 59.9999 -> DD = 59.9999 / 3600
    assert dd_to_dms_value(59.9999 / 3600.0) == (0, 1, 0.0)

    # Edge case: roll-over at minutes == 60
    # e.g., 0 degrees, 59 minutes, 59.9999 seconds
    # total seconds = 59 * 60 + 59.9999 = 3599.9999 -> DD = 3599.9999 / 3600
    assert dd_to_dms_value(3599.9999 / 3600.0) == (1, 0, 0.0)

def test_format_dms():
    # Latitude
    assert format_dms(45, 30, 0.0, is_lat=True) == "45°30'00.00\" N"
    assert format_dms(-45, 30, 0.0, is_lat=True) == "45°30'00.00\" S"

    # Longitude
    assert format_dms(122, 36, 0.0, is_lat=False) == "122°36'00.00\" E"
    assert format_dms(-122, 36, 0.0, is_lat=False) == "122°36'00.00\" W"

def test_convert_dd_to_dms():
    text_valid = "45.5, -122.6"
    result = convert_dd_to_dms(text_valid)
    assert "| Latitude (DD) | Longitude (DD) | Latitude (DMS) | Longitude (DMS) |" in result
    assert "45.5" in result
    assert "-122.6" in result
    assert "45°30'00.00\" N" in result
    assert "122°36'00.00\" W" in result

    # Invalid input
    result_invalid = convert_dd_to_dms("abc")
    assert "_Skipped invalid inputs:_" in result_invalid
