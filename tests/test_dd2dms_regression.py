import pytest
from dd2dms import dd_to_dms_value, format_dms

def test_dd_to_dms_value_rollover():
    val = 0.999999
    d, m, s = dd_to_dms_value(val)
    formatted = format_dms(d, m, s, True)
    assert '60.00"' not in formatted, f"Formatted string should not contain 60.00 seconds due to rollover bug, got {formatted}"
