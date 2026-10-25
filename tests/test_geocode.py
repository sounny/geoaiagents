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

def test_get_coordinates_first_result_on_multiple_candidates(mocker):
    import geocode
    mock_response = [
        {"place_id": 1, "lat": "40.0", "lon": "-70.0", "display_name": "First Place", "importance": 0.9, "class": "place", "type": "city"},
        {"place_id": 2, "lat": "41.0", "lon": "-71.0", "display_name": "Second Place", "importance": 0.8, "class": "place", "type": "city"}
    ]
    # Mock network calls to geocode API
    mocker.patch.object(geocode._geolocator.adapter, "get_json", return_value=mock_response)
    mocker.patch.object(geocode._geolocator.adapter, "get_text", return_value=mock_response)
    # Mock time.sleep to bypass RateLimiter delays
    mocker.patch("time.sleep")

    addr, lat, lon = geocode.get_coordinates("Mockville")
    assert addr == "First Place"
    assert lat == 40.0
    assert lon == -70.0


def test_get_coordinates_deepcopy_comparable(mocker, tmp_path, capsys):
    import geocode
    import copy
    from unittest.mock import MagicMock

    mock_location = MagicMock()
    mock_location.address = "Test Address"
    mock_location.latitude = 40.0
    mock_location.longitude = -70.0

    mocker.patch("geocode._geocode_limiter", return_value=mock_location)

    res = geocode.get_coordinates("Test")
    assert copy.deepcopy(res) == res

def test_parse_locations_deepcopy_comparable(mocker, tmp_path, capsys):
    import geocode
    import copy

    res = geocode.parse_locations("Test; Location")
    assert copy.deepcopy(res) == res

def test_reverse_geocode_coordinates_deepcopy_comparable(mocker, tmp_path, capsys):
    import geocode
    import copy
    from unittest.mock import MagicMock

    mock_location = MagicMock()
    mock_location.address = "Test Address"
    mock_location.latitude = 40.0
    mock_location.longitude = -70.0

    mocker.patch("geocode._reverse_limiter", return_value=mock_location)

    res = geocode.reverse_geocode_coordinates("40.0, -70.0")
    assert copy.deepcopy(res) == res

def test_geocode_locations_deepcopy_comparable(mocker, tmp_path, capsys):
    import geocode
    import copy
    from unittest.mock import MagicMock

    mock_location = MagicMock()
    mock_location.address = "Test Address"
    mock_location.latitude = 40.0
    mock_location.longitude = -70.0

    mocker.patch("geocode._geocode_limiter", return_value=mock_location)

    res = geocode.geocode_locations("Test")
    assert copy.deepcopy(res) == res

def test_main_deepcopy_comparable(mocker, tmp_path, capsys):
    import geocode
    import copy
    import json
    from unittest.mock import MagicMock
    import os

    # Use tmp_path for any potential filesystem writes (even if none exist, as requested)
    mocker.patch("os.chdir")
    os.chdir(str(tmp_path))

    mock_location = MagicMock()
    mock_location.address = "Test Address"
    mock_location.latitude = 40.0
    mock_location.longitude = -70.0

    mocker.patch("geocode._geocode_limiter", return_value=mock_location)
    mocker.patch("builtins.input", return_value="Test")
    mocker.patch("sys.argv", ["geocode.py"])

    mock_response = MagicMock()
    mock_message = MagicMock()

    mock_function_call = MagicMock()
    mock_function_call.name = "geocode_locations"
    mock_function_call.arguments = json.dumps({"locations": "Test"})
    mock_message.function_call = mock_function_call
    mock_message.content = "Test content"

    mock_response.choices = [MagicMock(message=mock_message)]
    mocker.patch("geocode.call_llm_with_retry", return_value=mock_response)
    mocker.patch("geocode.OpenAI")

    res = geocode.main()
    assert copy.deepcopy(res) == res
