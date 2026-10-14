import pytest
from geopy.exc import GeocoderTimedOut, GeocoderQuotaExceeded
from geocode import get_coordinates, reverse_geocode_coordinates, parse_locations, geocode_locations

def test_get_coordinates_timeout_or_error(mocker):
    # Mock _geocode_limiter to raise an exception
    mocker.patch("geocode._geocode_limiter", side_effect=Exception("Mocked timeout"))
    result = get_coordinates("Some location")
    assert result == (None, None, None)

def test_reverse_geocode_timeout_or_error(mocker):
    mocker.patch("geocode._reverse_limiter", side_effect=Exception("Mocked timeout"))
    result = reverse_geocode_coordinates("40.0, -70.0")
    assert "| 40.0 | -70.0 | Not found |" in result

def test_reverse_geocode_invalid_inputs():
    result = reverse_geocode_coordinates("abc, def; 100, 200")
    assert "_Skipped invalid inputs:_" in result
    assert "abc, def" in result
    assert "100, 200" in result

def test_parse_locations_mixed_delimiters_and_tabs_not_newline_only(mocker):
    mocker.patch("geocode._geocode_limiter", side_effect=AssertionError("No network calls allowed"))
    mocker.patch("geocode._reverse_limiter", side_effect=AssertionError("No network calls allowed"))
    assert parse_locations('Paris; London\nBerlin') == ['Paris', 'London', 'Berlin']
    assert parse_locations('  Tokyo  ;  ') == ['Tokyo']
    assert parse_locations('Lyon\tMarseille') == ['Lyon\tMarseille']
    assert parse_locations('   ') == []

def test_reverse_geocode_out_of_range_skipped_notes(mocker):
    mocker.patch("geocode._reverse_limiter", side_effect=AssertionError("No network calls allowed"))
    result = reverse_geocode_coordinates("91,0")
    assert "| Latitude | Longitude | Address |" in result
    assert "91,0" in result
    assert "_Skipped" in result or "Skipped" in result


@pytest.mark.parametrize("exc, expected_error_msg", [
    (GeocoderTimedOut("Mocked timeout"), "timeout"),
    (GeocoderQuotaExceeded("Mocked quota"), "quota"),
])
@pytest.mark.xfail(reason="Currently geocode.py suppresses geocoding errors and returns empty lat/lon")
def test_geocode_surfaces_clear_error_on_timeout_and_quota(mocker, exc, expected_error_msg):
    mocker.patch("geocode._geocode_limiter", side_effect=exc)

    try:
        result = geocode_locations("Paris")
    except Exception as e:
        # If it raises an exception, the error message should be clear
        assert expected_error_msg.lower() in str(e).lower()
        # and not a raw traceback (we just assert the string representation is concise enough or not purely a raw geopy error unless nicely formatted)
        # For simplicity, we just assert the keyword is in the exception message
        return

    # If it returns a result, the error should be surfaced in the returned string
    assert expected_error_msg.lower() in result.lower()
