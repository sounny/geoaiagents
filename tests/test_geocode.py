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

def test_geocode_empty_and_whitespace(mocker):
    import geocode
    mocker.patch("geocode._geocode_limiter", side_effect=AssertionError("No network calls allowed"))
    mocker.patch("geocode._reverse_limiter", side_effect=AssertionError("No network calls allowed"))

    # get_coordinates
    assert geocode.get_coordinates('') == (None, None, None)
    assert geocode.get_coordinates('   ') == (None, None, None)

    # get_coordinates returns empty when passed only whitespace/tabs/newlines because the external geocoder throws or returns empty
    assert geocode.get_coordinates('\t  \n') == (None, None, None)

    # For padded test, we need geocode.get_coordinates to actually receive the call,
    # but since our mock raises AssertionError, it will be caught and return (None, None, None)
    # To test stripping or propagation, we assert on the mock directly
    mocker.patch("geocode._geocode_limiter", return_value=mocker.Mock(address="Padded Place", latitude=10.0, longitude=20.0))
    assert geocode.get_coordinates('\t  Tokyo  \n') == ("Padded Place", 10.0, 20.0)

    # parse_locations
    assert geocode.parse_locations('') == []
    assert geocode.parse_locations('   ') == []
    assert geocode.parse_locations('\t  \n') == []
    assert geocode.parse_locations('\t  Tokyo  \n') == ['Tokyo']

    # reverse_geocode_coordinates
    mocker.patch("geocode._reverse_limiter", side_effect=AssertionError("No network calls allowed"))
    empty_res = "| Latitude | Longitude | Address |\n|---------:|----------:|---------|"
    assert geocode.reverse_geocode_coordinates('') == empty_res
    assert geocode.reverse_geocode_coordinates('   ') == empty_res
    assert geocode.reverse_geocode_coordinates('\t  \n') == empty_res

    mocker.patch("geocode._reverse_limiter", return_value=mocker.Mock(address="Padded Address"))
    assert "Padded Address" in geocode.reverse_geocode_coordinates('\t  40.0, -70.0  \n')

    # geocode_locations
    mocker.patch("geocode._geocode_limiter", side_effect=AssertionError("No network calls allowed"))
    empty_geo_res = "| Input | Matched Address | Latitude | Longitude |\n|-------|-----------------|----------|-----------|"
    assert geocode.geocode_locations('') == empty_geo_res
    assert geocode.geocode_locations('   ') == empty_geo_res
    assert geocode.geocode_locations('\t  \n') == empty_geo_res

    mocker.patch("geocode._geocode_limiter", return_value=mocker.Mock(address="Padded Geo", latitude=30.0, longitude=40.0))
    padded_res = geocode.geocode_locations('\t  Tokyo  \n')
    assert "Padded Geo" in padded_res
    assert "30.0" in padded_res
    assert "40.0" in padded_res
