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


@pytest.mark.xfail(reason="Bug: get_coordinates silently catches ValueError internally when timeout is True and incorrectly returns (None, None, None)")
def test_get_coordinates_bool_true_bug():
    from unittest.mock import patch
    import urllib3
    import pytest
    from geocode import get_coordinates
    with patch('urllib3.PoolManager.request') as mock_req, patch('time.sleep'):
        # Mock network so if it succeeds, we get a valid result.
        mock_req.return_value = urllib3.HTTPResponse(status=200, body=b'[{"place_id": 1, "lat": "40.0", "lon": "-70.0", "display_name": "First Place", "importance": 0.9, "class": "place", "type": "city"}]')
        get_coordinates.cache_clear()
        res = get_coordinates("London", timeout=True)
        # Because we passed timeout=True, urllib3 validation throws ValueError which is swallowed by the generic except.
        # This causes the valid mock response to never be reached and (None, None, None) is returned.
        if res == (None, None, None):
            pytest.fail("Bug: silently returns None instead of raising ValueError or returning results")

@pytest.mark.xfail(reason="Bug: get_coordinates silently catches ValueError internally when timeout is False and incorrectly returns (None, None, None)")
def test_get_coordinates_bool_false_bug():
    from unittest.mock import patch
    import urllib3
    import pytest
    from geocode import get_coordinates
    with patch('urllib3.PoolManager.request') as mock_req, patch('time.sleep'):
        mock_req.return_value = urllib3.HTTPResponse(status=200, body=b'[{"place_id": 1, "lat": "40.0", "lon": "-70.0", "display_name": "First Place", "importance": 0.9, "class": "place", "type": "city"}]')
        get_coordinates.cache_clear()
        res = get_coordinates("London", timeout=False)
        if res == (None, None, None):
            pytest.fail("Bug: silently returns None instead of raising ValueError or returning results")

@pytest.mark.xfail(reason="Bug: reverse_geocode_coordinates silently catches ValueError internally when timeout is True and incorrectly returns 'Not found'")
def test_reverse_geocode_coordinates_bool_true_bug():
    from unittest.mock import patch
    import urllib3
    import pytest
    from geocode import reverse_geocode_coordinates
    with patch('urllib3.PoolManager.request') as mock_req, patch('time.sleep'):
        mock_req.return_value = urllib3.HTTPResponse(status=200, body=b'{"place_id": 1, "lat": "40.0", "lon": "-70.0", "display_name": "Mocked Address", "importance": 0.9, "class": "place", "type": "city"}')
        res = reverse_geocode_coordinates("0,0", timeout=True)
        if "| 0.0 | 0.0 | Not found |" in res:
            pytest.fail("Bug: silently catches ValueError and returns 'Not found'")

@pytest.mark.xfail(reason="Bug: reverse_geocode_coordinates silently catches ValueError internally when timeout is False and incorrectly returns 'Not found'")
def test_reverse_geocode_coordinates_bool_false_bug():
    from unittest.mock import patch
    import urllib3
    import pytest
    from geocode import reverse_geocode_coordinates
    with patch('urllib3.PoolManager.request') as mock_req, patch('time.sleep'):
        mock_req.return_value = urllib3.HTTPResponse(status=200, body=b'{"place_id": 1, "lat": "40.0", "lon": "-70.0", "display_name": "Mocked Address", "importance": 0.9, "class": "place", "type": "city"}')
        res = reverse_geocode_coordinates("0,0", timeout=False)
        if "| 0.0 | 0.0 | Not found |" in res:
            pytest.fail("Bug: silently catches ValueError and returns 'Not found'")
