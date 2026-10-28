import pytest
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

@pytest.mark.parametrize("location_query", ["paris", "PARIS", "PaRiS"])
def test_get_coordinates_case_sensitivity(mocker, location_query):
    import geocode
    mock_response = [{"place_id": 1, "lat": "48.85", "lon": "2.35", "display_name": "Paris, France", "importance": 0.9, "class": "place", "type": "city"}]
    mocker.patch.object(geocode._geolocator.adapter, "get_json", return_value=mock_response)
    mocker.patch.object(geocode._geolocator.adapter, "get_text", return_value=mock_response)
    mocker.patch("time.sleep")

    # get_coordinates behavior is determined by the geolocator which operates in a case-insensitive manner.
    assert get_coordinates(location_query) == ("Paris, France", 48.85, 2.35)

@pytest.mark.parametrize("location_query", ["paris", "PARIS", "PaRiS"])
def test_parse_locations_case_sensitivity(location_query):
    # parse_locations retains the original case of the input
    assert parse_locations(location_query) == [location_query]

@pytest.mark.parametrize("coord_string", ["abc", "ABC", "aBc"])
def test_reverse_geocode_coordinates_case_sensitivity(coord_string):
    # reverse_geocode_coordinates outputs skipped invalid inputs maintaining the original case
    result = reverse_geocode_coordinates(coord_string)
    assert f"- `{coord_string}` (Missing latitude/longitude pair)" in result

@pytest.mark.parametrize("location_query", ["paris", "PARIS", "PaRiS"])
def test_geocode_locations_case_sensitivity(mocker, location_query):
    import geocode
    mock_response = [{"place_id": 1, "lat": "48.85", "lon": "2.35", "display_name": "Paris, France", "importance": 0.9, "class": "place", "type": "city"}]
    mocker.patch.object(geocode._geolocator.adapter, "get_json", return_value=mock_response)
    mocker.patch.object(geocode._geolocator.adapter, "get_text", return_value=mock_response)
    mocker.patch("time.sleep")

    # geocode_locations returns a table that includes the exact input string
    result = geocode_locations(location_query)
    assert f"| {location_query} |" in result
