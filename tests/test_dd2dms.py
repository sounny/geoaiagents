import pytest
from dd2dms import dd_to_dms_value

def test_dd_to_dms_rollover():
    # Test roll-over at seconds >= 59.9995
    # For example, 12.99999
    # 12 * 3600 = 43200
    # .99999 * 3600 = 3599.964 -> 59 mins, 59.964 seconds
    # Let's hit the boundary: 59 mins, 59.9995 seconds
    # .999999 * 3600 = 3599.9964 -> 59 mins, 59.9964 seconds

    # 1.0 degree = 60 mins
    # 0.9999999

    # Test cases:
    # 1. Standard calculation
    assert dd_to_dms_value(12.5) == (12, 30, 0.0)

    # 2. rollover from 59.9995+ seconds to 1 minute
    # 0.016666527777777778 degrees -> 0 degrees, 0 minutes, ~59.9995 seconds
    # 59.9995 / 3600 = 0.01666652777777778
    d, m, s = dd_to_dms_value(0.01666652777777778)
    assert d == 0
    assert m == 1
    assert s == 0.0

    # 3. rollover from 59 mins 59.9995+ seconds to 1 degree
    # 3599.9995 / 3600 = 0.9999998611111111
    d, m, s = dd_to_dms_value(0.9999998611111111)
    assert d == 1
    assert m == 0
    assert s == 0.0

    # 4. Negative numbers
    d, m, s = dd_to_dms_value(-0.9999998611111111)
    assert d == -1
    assert m == 0
    assert s == 0.0
