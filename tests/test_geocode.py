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

def test_get_coordinates_caplog(caplog, mocker):
    from geopy.exc import GeocoderTimedOut
    mocker.patch("geocode._geocode_limiter", side_effect=GeocoderTimedOut("Timed out"))
    from geocode import get_coordinates
    get_coordinates.cache_clear()
    get_coordinates("Paris")
    assert caplog.record_tuples == []

    mock_location = mocker.MagicMock()
    mock_location.address = "Paris"
    mock_location.latitude = 48.85
    mock_location.longitude = 2.35
    mocker.patch("geocode._geocode_limiter", return_value=mock_location)
    get_coordinates.cache_clear()
    get_coordinates("Paris")
    assert caplog.record_tuples == []

def test_reverse_geocode_coordinates_caplog(caplog, mocker):
    from geopy.exc import GeocoderTimedOut
    mocker.patch("geocode._reverse_limiter", side_effect=GeocoderTimedOut("Timed out"))
    from geocode import reverse_geocode_coordinates
    reverse_geocode_coordinates("40.0, -70.0")
    assert caplog.record_tuples == []

    mock_location = mocker.MagicMock()
    mock_location.address = "Paris"
    mocker.patch("geocode._reverse_limiter", return_value=mock_location)
    reverse_geocode_coordinates("40.0, -70.0")
    assert caplog.record_tuples == []

def test_geocode_locations_caplog(caplog, mocker):
    mocker.patch("geocode.get_coordinates", return_value=("Paris", 48.85, 2.35))
    from geocode import geocode_locations
    geocode_locations("Paris")
    assert caplog.record_tuples == []

def test_main_success_caplog(caplog, mocker, monkeypatch):
    import builtins
    mocker.patch.object(builtins, "input", return_value="Paris")
    mock_client = mocker.patch("geocode.OpenAI").return_value
    mock_response = mocker.MagicMock()
    mock_response.choices[0].message.function_call = None
    mock_response.choices[0].message.content = "Success"
    mock_client.chat.completions.create.return_value = mock_response
    mocker.patch("geocode.geocode_locations", return_value="Mock Table")
    import sys
    monkeypatch.setattr(sys, 'argv', ['geocode.py'])
    from geocode import main
    main()
    assert caplog.record_tuples == []

def test_main_error_caplog(caplog, mocker, monkeypatch):
    import builtins
    mocker.patch.object(builtins, "input", return_value="Paris")
    mock_client = mocker.patch("geocode.OpenAI").return_value
    mock_client.chat.completions.create.side_effect = Exception("API error")
    mocker.patch("geocode.geocode_locations", return_value="Mock Table")
    import sys
    monkeypatch.setattr(sys, 'argv', ['geocode.py'])
    from geocode import main
    main()
    log_names_levels = [(rec[0], rec[1]) for rec in caplog.record_tuples]
    assert log_names_levels == [('root', 30), ('root', 30), ('root', 40)]
