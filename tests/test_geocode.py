from unittest.mock import patch
import pytest
from geocode import get_coordinates, reverse_geocode_coordinates, parse_locations

@patch('geocode._geocode_limiter')
def test_get_coordinates_timeout_or_error(mock_geocode_limiter):
    # Mock _geocode_limiter to raise an exception
    mock_geocode_limiter.side_effect = Exception("Mocked timeout")
    result = get_coordinates("Some location")
    assert result == (None, None, None)

@patch('geocode._reverse_limiter')
def test_reverse_geocode_timeout_or_error(mock_reverse_limiter):
    mock_reverse_limiter.side_effect = Exception("Mocked timeout")
    result = reverse_geocode_coordinates("40.0, -70.0")
    assert "| 40.0 | -70.0 | Not found |" in result

def test_reverse_geocode_invalid_inputs():
    result = reverse_geocode_coordinates("abc, def; 100, 200")
    assert "_Skipped invalid inputs:_" in result
    assert "abc, def" in result
    assert "100, 200" in result

@patch('geocode._geocode_limiter')
@patch('geocode._reverse_limiter')
def test_parse_locations_mixed_delimiters_and_tabs_not_newline_only(mock_reverse_limiter, mock_geocode_limiter):
    mock_geocode_limiter.side_effect = AssertionError("No network calls allowed")
    mock_reverse_limiter.side_effect = AssertionError("No network calls allowed")
    assert parse_locations('Paris; London\nBerlin') == ['Paris', 'London', 'Berlin']
    assert parse_locations('  Tokyo  ;  ') == ['Tokyo']
    assert parse_locations('Lyon\tMarseille') == ['Lyon\tMarseille']
    assert parse_locations('   ') == []

@patch('geocode._reverse_limiter')
def test_reverse_geocode_out_of_range_skipped_notes(mock_reverse_limiter):
    mock_reverse_limiter.side_effect = AssertionError("No network calls allowed")
    result = reverse_geocode_coordinates("91,0")
    assert "| Latitude | Longitude | Address |" in result
    assert "91,0" in result
    assert "_Skipped" in result or "Skipped" in result

@patch('time.sleep')
@patch('geocode._geolocator.adapter.get_text')
@patch('geocode._geolocator.adapter.get_json')
def test_get_coordinates_first_result_on_multiple_candidates(mock_get_json, mock_get_text, mock_sleep):
    import geocode
    mock_response = [
        {"place_id": 1, "lat": "40.0", "lon": "-70.0", "display_name": "First Place", "importance": 0.9, "class": "place", "type": "city"},
        {"place_id": 2, "lat": "41.0", "lon": "-71.0", "display_name": "Second Place", "importance": 0.8, "class": "place", "type": "city"}
    ]
    # Mock network calls to geocode API
    mock_get_json.return_value = mock_response
    mock_get_text.return_value = mock_response
    # Mock time.sleep to bypass RateLimiter delays


    addr, lat, lon = geocode.get_coordinates("Mockville")
    assert addr == "First Place"
    assert lat == 40.0
    assert lon == -70.0

@pytest.mark.parametrize("ws_input", [" ", "\t", "\n", "\xa0"])
def test_whitespace_strings_parse_locations(ws_input):
    from geocode import parse_locations
    assert parse_locations(ws_input) == []

@pytest.mark.parametrize("ws_input", [" ", "\t", "\n", "\xa0"])
def test_whitespace_strings_reverse_geocode(ws_input):
    from geocode import reverse_geocode_coordinates
    result = reverse_geocode_coordinates(ws_input)
    assert "| Latitude" in result
    assert "Not found" not in result

@pytest.mark.parametrize("ws_input", [" ", "\t", "\n", "\xa0"])
@patch('geocode._geolocator.adapter.get_json')
def test_whitespace_strings_geocode_locations(mock_get_json, ws_input):
    from geocode import geocode_locations
    import geocode
    # mock to ensure no network call is made by parse_locations side effects

    result = geocode_locations(ws_input)
    assert "| Input" in result

@pytest.mark.xfail(reason="Bug: blindly queries API for whitespace-only strings instead of validating input")
@pytest.mark.parametrize("ws_input", [" ", "\t", "\n", "\xa0"])
@patch('geocode._geolocator.adapter.get_json')
def test_whitespace_strings_get_coordinates(mock_get_json, ws_input):
    import geocode

    geocode.get_coordinates(ws_input)
    # Asserting that the API should NOT be called for whitespace.
    # This will fail (triggering xfail) because it currently DOES call the API.
    mock_get_json.assert_not_called()

@pytest.mark.parametrize("ws_input", [" ", "\t", "\n", "\xa0"])
def test_whitespace_strings_parse_locations(ws_input):
    from geocode import parse_locations
    assert parse_locations(ws_input) == []

@pytest.mark.parametrize("ws_input", [" ", "\t", "\n", "\xa0"])
def test_whitespace_strings_reverse_geocode(mocker, ws_input):
    from geocode import reverse_geocode_coordinates
    import geocode
    # mock to ensure no network call is made
    mocker.patch("geocode._geocode_limiter")
    mocker.patch("geocode._reverse_limiter")
    result = reverse_geocode_coordinates(ws_input)
    assert "| Latitude" in result
    assert "Not found" not in result

@pytest.mark.parametrize("ws_input", [" ", "\t", "\n", "\xa0"])
def test_whitespace_strings_geocode_locations(mocker, ws_input):
    from geocode import geocode_locations
    import geocode
    # mock to ensure no network call is made
    mocker.patch("geocode._geocode_limiter")
    mocker.patch("geocode._reverse_limiter")
    result = geocode_locations(ws_input)
    assert "| Input" in result

@pytest.mark.xfail(reason="Bug: blindly queries API for whitespace-only strings instead of validating input")
@pytest.mark.parametrize("ws_input", [" ", "\t", "\n", "\xa0"])
def test_whitespace_strings_get_coordinates(mocker, ws_input):
    import geocode
    mock_get = mocker.patch("geocode._geocode_limiter")
    mocker.patch("time.sleep")
    geocode.get_coordinates(ws_input)
    # Asserting that the API should NOT be called for whitespace.
    # This will fail (triggering xfail) because it currently DOES call the API.
    mock_get.assert_not_called()

@pytest.mark.parametrize("ws_input", [" ", "\t", "\n", "\xa0"])
def test_whitespace_strings_parse_locations(ws_input):
    from geocode import parse_locations
    assert parse_locations(ws_input) == []

@pytest.mark.parametrize("ws_input", [" ", "\t", "\n", "\xa0"])
def test_whitespace_strings_reverse_geocode(mocker, ws_input):
    from geocode import reverse_geocode_coordinates
    # Ensure no network calls
    mocker.patch("geocode._reverse_limiter", side_effect=AssertionError("No network calls allowed"))
    result = reverse_geocode_coordinates(ws_input)
    assert "| Latitude" in result
    assert "Not found" not in result

@pytest.mark.parametrize("ws_input", [" ", "\t", "\n", "\xa0"])
def test_whitespace_strings_geocode_locations(mocker, ws_input):
    from geocode import geocode_locations
    # Ensure no network calls
    mocker.patch("geocode._geocode_limiter", side_effect=AssertionError("No network calls allowed"))
    result = geocode_locations(ws_input)
    assert "| Input" in result

@pytest.mark.xfail(reason="Bug: blindly queries API for whitespace-only strings instead of validating input")
@pytest.mark.parametrize("ws_input", [" ", "\t", "\n", "\xa0"])
def test_whitespace_strings_get_coordinates(mocker, ws_input):
    import geocode
    mock_get = mocker.patch("geocode._geocode_limiter")
    geocode.get_coordinates(ws_input)
    # Asserting that the API should NOT be called for whitespace.
    # This will fail (triggering xfail) because it currently DOES call the API.
    mock_get.assert_not_called()
