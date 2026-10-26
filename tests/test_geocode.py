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

@pytest.mark.parametrize(
    "func_name",
    [
        "call_llm_with_retry",
        "format_invalid_notes",
        pytest.param(
            "get_coordinates",
            marks=pytest.mark.xfail(raises=TypeError, reason="lru_cache wrapper does not support unhashable types like list")
        ),
    ]
)
def test_sequence_arguments_match_list_vs_tuple(mocker, tmp_path, func_name):
    mocker.patch("geocode._geocode_limiter")

    from unittest.mock import MagicMock
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = MagicMock(choices=[MagicMock(message="mock")])

    func_args = {
        'call_llm_with_retry': {'args': (mock_client,), 'kwargs_list': {'messages': [{"role": "user"}]}, 'kwargs_tuple': {'messages': ({"role": "user"},)}},
        'format_invalid_notes': {'args_list': ([("40", "nan")],), 'args_tuple': ((("40", "nan"),),), 'kwargs': {}},
        'get_coordinates': {'args': ("Paris",), 'kwargs_list': {'bounding_box': [1,2,3,4]}, 'kwargs_tuple': {'bounding_box': (1,2,3,4)}},
    }

    import geocode
    obj = getattr(geocode, func_name)
    info = func_args[func_name]

    args_l = info.get('args_list', info.get('args', ()))
    kwargs_l = info.get('kwargs_list', info.get('kwargs', {}))

    args_t = info.get('args_tuple', info.get('args', ()))
    kwargs_t = info.get('kwargs_tuple', info.get('kwargs', {}))

    res_l = obj(*args_l, **kwargs_l)
    res_t = obj(*args_t, **kwargs_t)
    assert res_l == res_t
