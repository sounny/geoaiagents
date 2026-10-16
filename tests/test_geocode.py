import pytest
import geocode
from geocode import get_coordinates, reverse_geocode_coordinates, parse_locations
from geopy.exc import GeocoderTimedOut
from geopy.extra.rate_limiter import RateLimiter

def test_get_coordinates_timeout_or_error(mocker):
    mock_geocode = mocker.MagicMock(side_effect=GeocoderTimedOut("Mocked HTTP timeout"))
    original_limiter = geocode._geocode_limiter
    try:
        geocode._geocode_limiter = RateLimiter(mock_geocode, min_delay_seconds=0, max_retries=2)
        result = get_coordinates("Some location")
        assert result == (None, None, None)
        assert mock_geocode.call_count == 3
    finally:
        geocode._geocode_limiter = original_limiter

def test_reverse_geocode_timeout_or_error(mocker):
    mock_reverse = mocker.MagicMock(side_effect=GeocoderTimedOut("Mocked HTTP timeout"))
    original_limiter = geocode._reverse_limiter
    try:
        geocode._reverse_limiter = RateLimiter(mock_reverse, min_delay_seconds=0, max_retries=2)
        result = reverse_geocode_coordinates("40.0, -70.0")
        assert "| 40.0 | -70.0 | Not found |" in result
        assert mock_reverse.call_count == 3
    finally:
        geocode._reverse_limiter = original_limiter

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
