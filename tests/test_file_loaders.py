import pytest
from file_loaders import load_csv, _table
from validation import format_invalid_notes

def test_load_csv_missing_lat_lon_columns():
    csv_text = "Name,City\nAlice,New York\nBob,Boston\nCharlie,Chicago"
    expected_notes = format_invalid_notes([
        ("Alice,New York", "Missing latitude/longitude columns"),
        ("Bob,Boston", "Missing latitude/longitude columns"),
        ("Charlie,Chicago", "Missing latitude/longitude columns")
    ])
    expected = _table([]) + expected_notes
    assert load_csv(csv_text) == expected

def test_load_csv_invalid_data():
    csv_text = "lat,lon,City\n40.7128,-74.0060,NYC\nbad,data,Boston\n41.8781,-87.6298,Chicago\nNone,None,LA"
    expected_notes = format_invalid_notes([
        ("bad,data,Boston", "Invalid coordinate data"),
        ("None,None,LA", "Invalid coordinate data")
    ])
    expected = _table([(40.7128, -74.0060), (41.8781, -87.6298)]) + expected_notes
    assert load_csv(csv_text) == expected

def test_load_csv_empty_or_header_only():
    empty_csv = ""
    assert load_csv(empty_csv) == _table([])

    header_only_no_latlon = "Name,City\n"
    assert load_csv(header_only_no_latlon) == _table([])

    header_only_with_latlon = "lat,lon,City\n"
    assert load_csv(header_only_with_latlon) == _table([])
