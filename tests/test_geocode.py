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

def test_geocode_unicode_and_emoji(mocker):
    from unittest.mock import MagicMock
    import geocode
    # Clear cache since lru_cache might remember previous calls
    geocode.get_coordinates.cache_clear()

    # Check parse_locations
    locations_str = "Montréal; 北京\n🌆"
    parsed = geocode.parse_locations(locations_str)
    assert parsed == ["Montréal", "北京", "🌆"]

    # Mock network calls to geocode API
    # Since we test geocode_locations which calls get_coordinates which uses _geocode_limiter
    def mock_geocode_call(query, **kwargs):
        if query == "Montréal":
            mock_loc = MagicMock()
            mock_loc.address = "Montreal, QC"
            mock_loc.latitude = 45.5019
            mock_loc.longitude = -73.5674
            return mock_loc
        elif query == "北京":
            mock_loc = MagicMock()
            mock_loc.address = "Beijing, China"
            mock_loc.latitude = 39.9042
            mock_loc.longitude = 116.4074
            return mock_loc
        else:
            return None

    mocker.patch("geocode._geocode_limiter", side_effect=mock_geocode_call)

    result = geocode.geocode_locations(locations_str)
    assert "| Montréal | Montreal, QC | 45.5019 | -73.5674 |" in result
    assert "| 北京 | Beijing, China | 39.9042 | 116.4074 |" in result
    assert "| 🌆 | Not found |  |  |" in result
