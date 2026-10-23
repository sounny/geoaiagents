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

def test_get_coordinates_parameters(mocker):
    import geocode
    geocode.get_coordinates.cache_clear()

    mock_response = [
        {"place_id": 1, "lat": "40.0", "lon": "-70.0", "display_name": "Mock Address", "importance": 0.9, "class": "place", "type": "city"}
    ]
    mocker.patch.object(geocode._geolocator.adapter, "get_json", return_value=mock_response)
    mocker.patch.object(geocode._geolocator.adapter, "get_text", return_value=mock_response)
    mocker.patch("time.sleep")

    # Optional parameters omitted
    geocode.get_coordinates.cache_clear()
    res1 = geocode.get_coordinates("Mockville")
    assert res1 == ("Mock Address", 40.0, -70.0)

    # Passed explicitly as their defaults
    geocode.get_coordinates.cache_clear()
    res2 = geocode.get_coordinates("Mockville", timeout=1, bounding_box=None, language="en")
    assert res2 == ("Mock Address", 40.0, -70.0)

    # Passed by keyword instead of position
    geocode.get_coordinates.cache_clear()
    res3 = geocode.get_coordinates(location_query="Mockville", timeout=1, bounding_box=None, language="en")
    assert res3 == ("Mock Address", 40.0, -70.0)

def test_reverse_geocode_coordinates_parameters(mocker):
    import geocode

    mock_response = {
        "place_id": 1, "lat": "40.0", "lon": "-70.0", "display_name": "Mock Address", "address": {"city": "Mock City"}
    }
    mocker.patch.object(geocode._geolocator.adapter, "get_json", return_value=mock_response)
    mocker.patch.object(geocode._geolocator.adapter, "get_text", return_value=mock_response)
    mocker.patch("time.sleep")

    # Optional parameters omitted
    res1 = geocode.reverse_geocode_coordinates("40.0, -70.0")
    assert "| 40.0 | -70.0 | Mock Address |" in res1

    # Passed explicitly as their defaults
    res2 = geocode.reverse_geocode_coordinates("40.0, -70.0", timeout=1, language="en")
    assert "| 40.0 | -70.0 | Mock Address |" in res2

    # Passed by keyword instead of position
    res3 = geocode.reverse_geocode_coordinates(coordinates_str="40.0, -70.0", timeout=1, language="en")
    assert "| 40.0 | -70.0 | Mock Address |" in res3

def test_parse_locations_parameters(mocker):
    import geocode
    mocker.patch("geocode._geocode_limiter", side_effect=AssertionError("No network calls allowed"))
    mocker.patch("geocode._reverse_limiter", side_effect=AssertionError("No network calls allowed"))

    # Optional parameters omitted (N/A, no optional parameters)
    res1 = geocode.parse_locations("A; B")
    assert res1 == ["A", "B"]

    # Passed by keyword instead of position
    res2 = geocode.parse_locations(locations_str="A; B")
    assert res2 == ["A", "B"]

def test_geocode_locations_parameters(mocker):
    import geocode
    geocode.get_coordinates.cache_clear()

    mock_response = [
        {"place_id": 1, "lat": "40.0", "lon": "-70.0", "display_name": "Mock Address", "importance": 0.9, "class": "place", "type": "city"}
    ]
    mocker.patch.object(geocode._geolocator.adapter, "get_json", return_value=mock_response)
    mocker.patch.object(geocode._geolocator.adapter, "get_text", return_value=mock_response)
    mocker.patch("time.sleep")

    # Optional parameters omitted (N/A)
    geocode.get_coordinates.cache_clear()
    res1 = geocode.geocode_locations("Mockville")
    assert "| Mockville | Mock Address | 40.0 | -70.0 |" in res1

    # Passed by keyword instead of position
    geocode.get_coordinates.cache_clear()
    res2 = geocode.geocode_locations(locations_str="Mockville")
    assert "| Mockville | Mock Address | 40.0 | -70.0 |" in res2

def test_main_parameters(mocker, capsys):
    import geocode
    mocker.patch("builtins.input", side_effect=["Mockville"])
    mocker.patch("sys.argv", ["geocode.py", "--base-url", "http://test", "--api-key", "test"])

    mock_response = [
        {"place_id": 1, "lat": "40.0", "lon": "-70.0", "display_name": "Mock Address", "importance": 0.9, "class": "place", "type": "city"}
    ]
    mocker.patch.object(geocode._geolocator.adapter, "get_json", return_value=mock_response)
    mocker.patch.object(geocode._geolocator.adapter, "get_text", return_value=mock_response)
    mocker.patch("time.sleep")

    # mock call_llm_with_retry to simulate exception so it falls back to local
    mocker.patch("geocode.call_llm_with_retry", side_effect=Exception("API Error"))

    geocode.get_coordinates.cache_clear()
    # Main has no parameters, just calling it to cover it
    geocode.main()

    captured = capsys.readouterr()
    assert "Mock Address" in captured.out
    assert "| 40.0 | -70.0 |" in captured.out
