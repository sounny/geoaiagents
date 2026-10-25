import pytest
import warnings
import geocode
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


def test_get_coordinates_no_warnings(mocker, tmp_path):
    mocker.patch("geocode._geocode_limiter", return_value=mocker.MagicMock(address="London", latitude=51.5, longitude=-0.1))
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        geocode.get_coordinates("London")

def test_parse_locations_no_warnings(mocker, tmp_path):
    test_file = tmp_path / "locations.txt"
    test_file.write_text("London\nParis")
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        geocode.parse_locations(test_file.read_text())

def test_reverse_geocode_coordinates_no_warnings(mocker, tmp_path):
    mocker.patch("geocode._reverse_limiter", return_value=mocker.MagicMock(address="Somewhere"))
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        geocode.reverse_geocode_coordinates("51.5, -0.1")

def test_geocode_locations_no_warnings(mocker, tmp_path):
    mocker.patch("geocode.get_coordinates", return_value=("London", 51.5, -0.1))
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        geocode.geocode_locations("London")

def test_main_no_warnings(mocker, tmp_path):
    test_file = tmp_path / "locations.txt"
    test_file.write_text("London")
    mocker.patch("builtins.input", return_value=test_file.read_text())
    mocker.patch("sys.argv", ["geocode.py"])
    mock_response = mocker.MagicMock()
    mock_response.choices = [mocker.MagicMock(message=mocker.MagicMock(function_call=None, content="Hi"))]
    mocker.patch("geocode.call_llm_with_retry", return_value=mock_response)
    mocker.patch("geocode.geocode_locations", return_value="Table")
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        geocode.main()
