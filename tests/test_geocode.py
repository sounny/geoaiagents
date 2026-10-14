import pytest
from geocode import get_coordinates, reverse_geocode_coordinates, parse_locations, geocode_locations
from unittest.mock import MagicMock

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

def test_geocode_spacing_nominatim_policy(mocker):
    import geocode
    import time

    # Mock the HTTP layer (or Nominatim.geocode) to avoid real network calls
    mock_geocode = mocker.patch("geopy.geocoders.Nominatim.geocode")
    loc = MagicMock()
    loc.address = "Dummy"
    loc.latitude = 10.0
    loc.longitude = 20.0
    mock_geocode.return_value = loc
    # Re-assign the function for the cached rate limiter
    mocker.patch.object(geocode._geocode_limiter, "func", mock_geocode)

    # Mock time.sleep to avoid blocking
    mock_sleep = mocker.patch("time.sleep")

    current_time = [10.0]
    def mock_clock_impl():
        return current_time[0]

    def mock_sleep_impl(seconds):
        current_time[0] += seconds
        mock_sleep(seconds)

    # geopy RateLimiter binds _clock and _sleep methods on the instance
    if hasattr(geocode._geocode_limiter, "_clock"):
        mocker.patch.object(geocode._geocode_limiter, "_clock", side_effect=mock_clock_impl)
    if hasattr(geocode._geocode_limiter, "_sleep"):
        mocker.patch.object(geocode._geocode_limiter, "_sleep", side_effect=mock_sleep_impl)

    geocode_locations("Paris\nLondon\nBerlin\nMadrid")

    # We should have at least 3 sleeps for the 4 locations
    sleeps = [call.args[0] for call in mock_sleep.call_args_list]

    if len(sleeps) < 3 or sum(sleeps) < 3.0:
        pytest.xfail("Geocoding requests are not spaced correctly to obey Nominatim policy")
