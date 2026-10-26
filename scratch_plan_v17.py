import pytest
import math
from geocode import get_coordinates, reverse_geocode_coordinates

@pytest.mark.parametrize("timeout, expected_error", [
    pytest.param(float("nan"), ValueError, marks=pytest.mark.xfail(raises=AssertionError, strict=True, reason="Bug: get_coordinates swallows ValueError for nan timeout")),
    pytest.param(float("inf"), OverflowError, marks=pytest.mark.xfail(raises=AssertionError, strict=True, reason="Bug: get_coordinates swallows OverflowError for inf timeout")),
    pytest.param(float("-inf"), OverflowError, marks=pytest.mark.xfail(raises=AssertionError, strict=True, reason="Bug: get_coordinates swallows OverflowError for -inf timeout")),
    (-0.0, None)
])
def test_get_coordinates_special_floats(mocker, tmp_path, monkeypatch, timeout, expected_error):
    monkeypatch.chdir(tmp_path)

    mock_response = [{"place_id": 1, "lat": "40.0", "lon": "-70.0", "display_name": "Mocked Address", "importance": 0.9, "class": "place", "type": "city"}]

    def mock_get_json(url, timeout, headers=None, **kwargs):
        if type(timeout) is float and math.isnan(timeout):
            raise ValueError("Timeout is NaN")
        if type(timeout) is float and math.isinf(timeout):
            raise OverflowError("Timeout is inf")
        return mock_response

    mocker.patch("geocode._geolocator.adapter.get_json", side_effect=mock_get_json)
    mocker.patch("geocode._geolocator.adapter.get_text", side_effect=mock_get_json)

    get_coordinates.cache_clear()

    if expected_error:
        try:
            get_coordinates("Paris", timeout=timeout)
        except expected_error:
            # Bug fixed! The native error was successfully raised.
            pass
        else:
            # Bug still present. The error was swallowed (e.g. by geocode.py returning None).
            # Force an AssertionError to fulfill the xfail condition.
            assert False, f"Expected {expected_error.__name__} to be raised, but it was swallowed"
    else:
        res = get_coordinates("Paris", timeout=timeout)
        assert res == ("Mocked Address", 40.0, -70.0)

@pytest.mark.parametrize("timeout, expected_error", [
    pytest.param(float("nan"), ValueError, marks=pytest.mark.xfail(raises=AssertionError, strict=True, reason="Bug: geocode swallows ValueError for nan timeout")),
    pytest.param(float("inf"), OverflowError, marks=pytest.mark.xfail(raises=AssertionError, strict=True, reason="Bug: geocode swallows OverflowError for inf timeout")),
    pytest.param(float("-inf"), OverflowError, marks=pytest.mark.xfail(raises=AssertionError, strict=True, reason="Bug: geocode swallows OverflowError for -inf timeout")),
    (-0.0, None)
])
def test_reverse_geocode_coordinates_special_floats(mocker, tmp_path, monkeypatch, timeout, expected_error):
    monkeypatch.chdir(tmp_path)

    mock_response = {"place_id": 1, "lat": "40.0", "lon": "-70.0", "display_name": "Mocked Address", "importance": 0.9, "class": "place", "type": "city"}

    def mock_get_json(url, timeout, headers=None, **kwargs):
        if type(timeout) is float and math.isnan(timeout):
            raise ValueError("Timeout is NaN")
        if type(timeout) is float and math.isinf(timeout):
            raise OverflowError("Timeout is inf")
        return mock_response

    mocker.patch("geocode._geolocator.adapter.get_json", side_effect=mock_get_json)
    mocker.patch("geocode._geolocator.adapter.get_text", side_effect=mock_get_json)

    if expected_error:
        try:
            reverse_geocode_coordinates("40.0, -70.0", timeout=timeout)
        except expected_error:
            pass
        else:
            assert False, f"Expected {expected_error.__name__} to be raised, but it was swallowed"
    else:
        res = reverse_geocode_coordinates("40.0, -70.0", timeout=timeout)
        assert "Mocked Address" in res
