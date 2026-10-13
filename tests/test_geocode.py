import pytest
from geocode import get_coordinates, reverse_geocode_coordinates, parse_locations

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

def test_geocode_locations_empty_and_whitespace(mocker):
    mocker.patch("geocode._geocode_limiter", side_effect=AssertionError("No network calls allowed"))

    # Test empty
    result = __import__("geocode").geocode_locations('')
    assert "| Input | Matched Address | Latitude | Longitude |" in result
    assert "|-------|-----------------|----------|-----------|" in result
    # It shouldn't add any rows because parse_locations('') returns []
    assert len(result.split('\n')) == 2

    # Test whitespace
    result2 = __import__("geocode").geocode_locations('   ')
    assert "| Input | Matched Address | Latitude | Longitude |" in result2
    assert "|-------|-----------------|----------|-----------|" in result2
    assert len(result2.split('\n')) == 2

def test_geocode_locations_mocked_provider_no_results(mocker):
    # Mock to return nothing (None)
    mocker.patch("geocode._geocode_limiter", return_value=None)

    result = __import__("geocode").geocode_locations('Atlantis')
    assert "| Input | Matched Address | Latitude | Longitude |" in result
    assert "| Atlantis | Not found |  |  |" in result
