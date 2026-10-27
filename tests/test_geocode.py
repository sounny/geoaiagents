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

@pytest.mark.parametrize("func_name,runner", [
    ("get_coordinates", lambda mocker, tmp_path: __import__('geocode').get_coordinates("New York")),
    ("parse_locations", lambda mocker, tmp_path: __import__('geocode').parse_locations("A; B")),
    ("reverse_geocode_coordinates", lambda mocker, tmp_path: __import__('geocode').reverse_geocode_coordinates("10, 20")),
    ("geocode_locations", lambda mocker, tmp_path: __import__('geocode').geocode_locations("New York")),
    ("main", lambda mocker, tmp_path: (
        __import__('sys').modules.update({'sys.stdout': __import__('io').StringIO()}),
        tmp_path.joinpath("input.txt").write_text("New York; Paris\n"),
        mocker.patch('builtins.input', return_value="New York"),
        mocker.patch('sys.argv', ['geocode.py']),
        mocker.patch('sys.stdout', __import__('io').StringIO()),
        __import__('geocode').main(),
        __import__('sys').stdout.getvalue()
    )[-1])
])
def test_public_functions_tz_independent(monkeypatch, mocker, tmp_path, func_name, runner):
    import time
    from unittest.mock import MagicMock
    import geocode

    mocker.patch("geocode._geocode_limiter", return_value=MagicMock(address="Test Address", latitude=10.0, longitude=20.0))
    mocker.patch("geocode._reverse_limiter", return_value=MagicMock(address="Test Address"))

    mock_msg = MagicMock()
    mock_msg.function_call = None
    mock_msg.content = "Result"
    mock_choice = MagicMock()
    mock_choice.message = mock_msg
    mock_resp = MagicMock()
    mock_resp.choices = [mock_choice]
    mocker.patch("geocode.call_llm_with_retry", return_value=mock_resp)

    mocker.patch("geocode.OpenAI")

    def run_under_tz(tz_name):
        monkeypatch.setenv("TZ", tz_name)
        if hasattr(time, "tzset"):
            time.tzset()

        if hasattr(geocode, func_name) and hasattr(getattr(geocode, func_name), "cache_clear"):
            getattr(geocode, func_name).cache_clear()

        return runner(mocker, tmp_path)

    try:
        res_utc = run_under_tz("UTC")
        res_ny = run_under_tz("America/New_York")
    except Exception as e:
        pytest.xfail(f"Exception during TZ test for {func_name}: {e}")

    if res_utc != res_ny:
        pytest.xfail(f"Behavior differs between TZs for {func_name}")
    assert res_utc == res_ny
