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

def test_boundaries(mocker):
    import geocode
    mocker.patch("geocode._geocode_limiter", return_value=None)
    mocker.patch("geocode._reverse_limiter", return_value=None)

    assert geocode.parse_locations("") == []
    assert geocode.get_coordinates("") == (None, None, None)
    assert geocode.reverse_geocode_coordinates("") == "| Latitude | Longitude | Address |\n|---------:|----------:|---------|"
    assert geocode.geocode_locations("") == "| Input | Matched Address | Latitude | Longitude |\n|-------|-----------------|----------|-----------|"

    assert geocode.parse_locations("0") == ["0"]
    assert geocode.get_coordinates("0") == (None, None, None)
    assert geocode.reverse_geocode_coordinates("0") == "| Latitude | Longitude | Address |\n|---------:|----------:|---------|\n_Skipped invalid inputs:_\n- `0` (Missing latitude/longitude pair)"
    assert geocode.geocode_locations("0") == "| Input | Matched Address | Latitude | Longitude |\n|-------|-----------------|----------|-----------|\n| 0 | Not found |  |  |"

    assert geocode.parse_locations("1") == ["1"]
    assert geocode.get_coordinates("1") == (None, None, None)
    assert geocode.reverse_geocode_coordinates("1") == "| Latitude | Longitude | Address |\n|---------:|----------:|---------|\n_Skipped invalid inputs:_\n- `1` (Missing latitude/longitude pair)"
    assert geocode.geocode_locations("1") == "| Input | Matched Address | Latitude | Longitude |\n|-------|-----------------|----------|-----------|\n| 1 | Not found |  |  |"

    large_str = "A" * 10000
    assert geocode.parse_locations(large_str) == [large_str]
    assert geocode.get_coordinates(large_str) == (None, None, None)
    assert geocode.reverse_geocode_coordinates(large_str) == f"| Latitude | Longitude | Address |\n|---------:|----------:|---------|\n_Skipped invalid inputs:_\n- `{large_str}` (Missing latitude/longitude pair)"
    assert geocode.geocode_locations(large_str) == f"| Input | Matched Address | Latitude | Longitude |\n|-------|-----------------|----------|-----------|\n| {large_str} | Not found |  |  |"

    unicode_str = "こんにちは"
    assert geocode.parse_locations(unicode_str) == [unicode_str]
    assert geocode.get_coordinates(unicode_str) == (None, None, None)
    assert geocode.reverse_geocode_coordinates(unicode_str) == f"| Latitude | Longitude | Address |\n|---------:|----------:|---------|\n_Skipped invalid inputs:_\n- `{unicode_str}` (Missing latitude/longitude pair)"
    assert geocode.geocode_locations(unicode_str) == f"| Input | Matched Address | Latitude | Longitude |\n|-------|-----------------|----------|-----------|\n| {unicode_str} | Not found |  |  |"

    assert geocode.parse_locations("0,0") == ["0,0"]
    assert geocode.get_coordinates("0,0") == (None, None, None)
    assert geocode.reverse_geocode_coordinates("0,0") == "| Latitude | Longitude | Address |\n|---------:|----------:|---------|\n| 0.0 | 0.0 | Not found |"
    assert geocode.geocode_locations("0,0") == "| Input | Matched Address | Latitude | Longitude |\n|-------|-----------------|----------|-----------|\n| 0,0 | Not found |  |  |"

    assert geocode.parse_locations("-90, -180") == ["-90, -180"]
    assert geocode.get_coordinates("-90, -180") == (None, None, None)
    assert geocode.reverse_geocode_coordinates("-90, -180") == "| Latitude | Longitude | Address |\n|---------:|----------:|---------|\n| -90.0 | -180.0 | Not found |"
    assert geocode.geocode_locations("-90, -180") == "| Input | Matched Address | Latitude | Longitude |\n|-------|-----------------|----------|-----------|\n| -90, -180 | Not found |  |  |"

    assert geocode.parse_locations("90, 180") == ["90, 180"]
    assert geocode.get_coordinates("90, 180") == (None, None, None)
    assert geocode.reverse_geocode_coordinates("90, 180") == "| Latitude | Longitude | Address |\n|---------:|----------:|---------|\n| 90.0 | 180.0 | Not found |"
    assert geocode.geocode_locations("90, 180") == "| Input | Matched Address | Latitude | Longitude |\n|-------|-----------------|----------|-----------|\n| 90, 180 | Not found |  |  |"

    assert geocode.parse_locations("-90.00000000000001, -180.00000000000001") == ["-90.00000000000001, -180.00000000000001"]
    assert geocode.get_coordinates("-90.00000000000001, -180.00000000000001") == (None, None, None)
    assert geocode.reverse_geocode_coordinates("-90.00000000000001, -180.00000000000001") == "| Latitude | Longitude | Address |\n|---------:|----------:|---------|\n_Skipped invalid inputs:_\n- `-90.00000000000001, -180.00000000000001` (Out of range (-90 <= lat <= 90, -180 <= lon <= 180))"
    assert geocode.geocode_locations("-90.00000000000001, -180.00000000000001") == "| Input | Matched Address | Latitude | Longitude |\n|-------|-----------------|----------|-----------|\n| -90.00000000000001, -180.00000000000001 | Not found |  |  |"

    assert geocode.parse_locations("90.00000000000001, 180.00000000000001") == ["90.00000000000001, 180.00000000000001"]
    assert geocode.get_coordinates("90.00000000000001, 180.00000000000001") == (None, None, None)
    assert geocode.reverse_geocode_coordinates("90.00000000000001, 180.00000000000001") == "| Latitude | Longitude | Address |\n|---------:|----------:|---------|\n_Skipped invalid inputs:_\n- `90.00000000000001, 180.00000000000001` (Out of range (-90 <= lat <= 90, -180 <= lon <= 180))"
    assert geocode.geocode_locations("90.00000000000001, 180.00000000000001") == "| Input | Matched Address | Latitude | Longitude |\n|-------|-----------------|----------|-----------|\n| 90.00000000000001, 180.00000000000001 | Not found |  |  |"
