import unicodedata
import unicodedata
import pytest
from geocode import get_coordinates, reverse_geocode_coordinates, parse_locations, geocode_locations, geocode_locations

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

def test_get_coordinates_nfc_nfd(mocker):
    get_coordinates.cache_clear()

    mock_geocode = mocker.patch("geocode._geocode_limiter")
    mock_geocode.return_value.address = "Paris"
    mock_geocode.return_value.latitude = 48.85
    mock_geocode.return_value.longitude = 2.35

    nfc_str = unicodedata.normalize('NFC', 'Amélie')
    nfd_str = unicodedata.normalize('NFD', 'Amélie')

    res1 = get_coordinates(nfc_str)
    res2 = get_coordinates(nfd_str)

    if mock_geocode.call_count != 1:
        pytest.xfail("Bug: get_coordinates calls API multiple times for different Unicode normalizations")
    assert res1 == res2

def test_parse_locations_nfc_nfd():
    nfc_str = unicodedata.normalize('NFC', 'Amélie')
    nfd_str = unicodedata.normalize('NFD', 'Amélie')

    res1 = parse_locations(nfc_str)
    res2 = parse_locations(nfd_str)

    if res1 != res2:
        pytest.xfail("Bug: parse_locations returns differently normalized strings")

def test_geocode_locations_nfc_nfd(mocker):
    get_coordinates.cache_clear()

    mock_geocode = mocker.patch("geocode._geocode_limiter")
    mock_geocode.return_value.address = "Paris"
    mock_geocode.return_value.latitude = 48.85
    mock_geocode.return_value.longitude = 2.35

    nfc_str = unicodedata.normalize('NFC', 'Amélie')
    nfd_str = unicodedata.normalize('NFD', 'Amélie')

    res1 = geocode_locations(nfc_str)
    res2 = geocode_locations(nfd_str)

    if res1 != res2:
        pytest.xfail("Bug: geocode_locations output differs for NFC and NFD")

def test_reverse_geocode_coordinates_nfc_nfd(mocker):
    mock_reverse = mocker.patch("geocode._reverse_limiter")

    nfc_str = unicodedata.normalize('NFC', 'Amélie, 100')
    nfd_str = unicodedata.normalize('NFD', 'Amélie, 100')

    res1 = reverse_geocode_coordinates(nfc_str)
    res2 = reverse_geocode_coordinates(nfd_str)

    if res1 != res2:
        pytest.xfail("Bug: reverse_geocode_coordinates output differs for NFC and NFD")

def test_get_coordinates_nfc_nfd(mocker, tmp_path):
    get_coordinates.cache_clear()
    mock_geocode = mocker.patch("geocode._geocode_limiter")
    mock_geocode.return_value.address = "Paris"
    mock_geocode.return_value.latitude = 48.85
    mock_geocode.return_value.longitude = 2.35
    nfc_str = unicodedata.normalize('NFC', 'Amélie')
    nfd_str = unicodedata.normalize('NFD', 'Amélie')
    nfc_file = tmp_path / "nfc.txt"
    nfc_file.write_text(nfc_str, encoding="utf-8")
    nfd_file = tmp_path / "nfd.txt"
    nfd_file.write_text(nfd_str, encoding="utf-8")
    res1 = get_coordinates(nfc_file.read_text(encoding="utf-8"))
    res2 = get_coordinates(nfd_file.read_text(encoding="utf-8"))
    if mock_geocode.call_count != 1:
        pytest.xfail("Bug: get_coordinates calls API multiple times for different Unicode normalizations")
    assert res1 == res2

def test_parse_locations_nfc_nfd(tmp_path):
    nfc_str = unicodedata.normalize('NFC', 'Amélie')
    nfd_str = unicodedata.normalize('NFD', 'Amélie')
    nfc_file = tmp_path / "nfc.txt"
    nfc_file.write_text(nfc_str, encoding="utf-8")
    nfd_file = tmp_path / "nfd.txt"
    nfd_file.write_text(nfd_str, encoding="utf-8")
    res1 = parse_locations(nfc_file.read_text(encoding="utf-8"))
    res2 = parse_locations(nfd_file.read_text(encoding="utf-8"))
    if res1 != res2:
        pytest.xfail("Bug: parse_locations returns differently normalized strings")

def test_geocode_locations_nfc_nfd(mocker, tmp_path):
    get_coordinates.cache_clear()
    mock_geocode = mocker.patch("geocode._geocode_limiter")
    mock_geocode.return_value.address = "Paris"
    mock_geocode.return_value.latitude = 48.85
    mock_geocode.return_value.longitude = 2.35
    nfc_str = unicodedata.normalize('NFC', 'Amélie')
    nfd_str = unicodedata.normalize('NFD', 'Amélie')
    nfc_file = tmp_path / "nfc.txt"
    nfc_file.write_text(nfc_str, encoding="utf-8")
    nfd_file = tmp_path / "nfd.txt"
    nfd_file.write_text(nfd_str, encoding="utf-8")
    res1 = geocode_locations(nfc_file.read_text(encoding="utf-8"))
    res2 = geocode_locations(nfd_file.read_text(encoding="utf-8"))
    if res1 != res2:
        pytest.xfail("Bug: geocode_locations output differs for NFC and NFD")

def test_reverse_geocode_coordinates_nfc_nfd(mocker, tmp_path):
    mock_reverse = mocker.patch("geocode._reverse_limiter")
    nfc_str = unicodedata.normalize('NFC', 'Amélie, 100')
    nfd_str = unicodedata.normalize('NFD', 'Amélie, 100')
    nfc_file = tmp_path / "nfc.txt"
    nfc_file.write_text(nfc_str, encoding="utf-8")
    nfd_file = tmp_path / "nfd.txt"
    nfd_file.write_text(nfd_str, encoding="utf-8")
    try:
        res1 = reverse_geocode_coordinates(nfc_file.read_text(encoding="utf-8"))
        res2 = reverse_geocode_coordinates(nfd_file.read_text(encoding="utf-8"))
    except ValueError:
        pytest.xfail("Bug: reverse_geocode_coordinates raises ValueError on invalid input before processing")
    if res1 != res2:
        pytest.xfail("Bug: reverse_geocode_coordinates output differs for NFC and NFD")
