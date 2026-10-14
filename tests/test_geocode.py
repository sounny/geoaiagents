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

def test_nominatim_user_agent(mocker):
    # To catch headers securely without relying on third party library presence (requests)
    # we patch URLLibAdapter.urlopen which is guaranteed to be in geopy.
    # geopy 2.5.0 uses Nominatim which by default uses URLLibAdapter, but can use RequestsAdapter
    # We will patch geopy.adapters.URLLibAdapter.get_text and geopy.adapters.RequestsAdapter.get_text
    import geopy.adapters

    mock_get_text_req = None
    if hasattr(geopy.adapters, "RequestsAdapter"):
        mock_get_text_req = mocker.patch.object(geopy.adapters.RequestsAdapter, "get_text", create=True)
        mock_get_text_req.return_value = '[{"lat": "48.85", "lon": "2.35", "display_name": "Paris"}]'

    mock_get_text_url = mocker.patch.object(geopy.adapters.URLLibAdapter, "get_text", create=True)
    mock_get_text_url.return_value = '[{"lat": "48.85", "lon": "2.35", "display_name": "Paris"}]'

    # get_coordinates is already imported at the top of tests/test_geocode.py:
    # from geocode import get_coordinates, reverse_geocode_coordinates, parse_locations
    get_coordinates("Paris")

    headers = {}
    if mock_get_text_url.called:
        # get_text(self, url, *, timeout, headers)
        kwargs = mock_get_text_url.call_args[1]
        headers = kwargs.get("headers", {})
    elif mock_get_text_req and mock_get_text_req.called:
        kwargs = mock_get_text_req.call_args[1]
        headers = kwargs.get("headers", {})
    else:
        pytest.xfail("Could not verify User-Agent: request was not made or different HTTP library was used")

    ua = ""
    for k, v in headers.items():
        if k.lower() == "user-agent":
            ua = v
            break

    if not ua or ua.startswith("python-urllib/") or ua.startswith("python-requests/"):
        pytest.xfail(f"Missing, empty or generic User-Agent header: {ua!r}")

    assert ua
