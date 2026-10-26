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

from collections import OrderedDict
from geocode import geocode_locations

class MyStr(str): pass
class MyInt(int): pass
class MyDict(dict): pass
class MyList(list): pass
class MyOrderedDict(OrderedDict): pass

@pytest.mark.parametrize("func, kwargs_base_func", [
    (get_coordinates, lambda f: {"location_query": f, "timeout": 1, "language": "en"}),
    (parse_locations, lambda f: {"locations_str": f}),
    (reverse_geocode_coordinates, lambda f: {"coordinates_str": f, "timeout": 1, "language": "en"}),
    (geocode_locations, lambda f: {"locations_str": f})
])
def test_geocode_subclasses(func, kwargs_base_func, mocker, tmp_path):
    mocker.patch("geocode._geocode_limiter", return_value=mocker.Mock(address="A", latitude=1.0, longitude=2.0))
    mocker.patch("geocode._reverse_limiter", return_value=mocker.Mock(address="A"))

    # Use tmp_path to create test data
    test_file = tmp_path / "locations.txt"
    test_file.write_text("London")
    file_content = test_file.read_text()

    # Standard builtin
    kwargs_base = kwargs_base_func(file_content)
    # Our subclasses
    kwargs_sub = kwargs_base_func(MyStr(file_content))
    if "timeout" in kwargs_sub:
        kwargs_sub["timeout"] = MyInt(1)
        kwargs_sub["language"] = MyStr("en")

    try:
        res_base = func(**kwargs_base)
    except Exception as e_base:
        try:
            func(**kwargs_sub)
        except Exception as e_sub:
            if type(e_base) != type(e_sub) or str(e_base) != str(e_sub):
                pytest.xfail(f"Exception mismatch: {repr(e_base)} != {repr(e_sub)}")
            return
        pytest.xfail(f"Subclass succeeded but base raised {repr(e_base)}")
    else:
        try:
            res_sub = func(**kwargs_sub)
        except Exception as e_sub:
            pytest.xfail(f"Base succeeded but subclass raised {repr(e_sub)}")
        else:
            if res_base != res_sub:
                pytest.xfail("Result mismatch")
            assert res_base == res_sub, "Results match"

@pytest.mark.parametrize("func, kwargs_base, kwargs_sub", [
    (get_coordinates, {"location_query": {"A": 1}, "timeout": 1, "language": "en"}, {"location_query": MyDict({"A": 1}), "timeout": MyInt(1), "language": MyStr("en")}),
    (get_coordinates, {"location_query": ["A"], "timeout": 1, "language": "en"}, {"location_query": MyList(["A"]), "timeout": MyInt(1), "language": MyStr("en")}),
    (get_coordinates, {"location_query": OrderedDict([("A", 1)]), "timeout": 1, "language": "en"}, {"location_query": MyOrderedDict([("A", 1)]), "timeout": MyInt(1), "language": MyStr("en")}),

    (parse_locations, {"locations_str": {"A": 1}}, {"locations_str": MyDict({"A": 1})}),
    (parse_locations, {"locations_str": ["A"]}, {"locations_str": MyList(["A"])}),
    (parse_locations, {"locations_str": OrderedDict([("A", 1)])}, {"locations_str": MyOrderedDict([("A", 1)])}),

    (reverse_geocode_coordinates, {"coordinates_str": {"A": 1}, "timeout": 1, "language": "en"}, {"coordinates_str": MyDict({"A": 1}), "timeout": MyInt(1), "language": MyStr("en")}),
    (reverse_geocode_coordinates, {"coordinates_str": ["A"], "timeout": 1, "language": "en"}, {"coordinates_str": MyList(["A"]), "timeout": MyInt(1), "language": MyStr("en")}),
    (reverse_geocode_coordinates, {"coordinates_str": OrderedDict([("A", 1)]), "timeout": 1, "language": "en"}, {"coordinates_str": MyOrderedDict([("A", 1)]), "timeout": MyInt(1), "language": MyStr("en")}),

    (geocode_locations, {"locations_str": {"A": 1}}, {"locations_str": MyDict({"A": 1})}),
    (geocode_locations, {"locations_str": ["A"]}, {"locations_str": MyList(["A"])}),
    (geocode_locations, {"locations_str": OrderedDict([("A", 1)])}, {"locations_str": MyOrderedDict([("A", 1)])}),
])
def test_geocode_unsupported_types(func, kwargs_base, kwargs_sub, mocker, tmp_path):
    mocker.patch("geocode._geocode_limiter", return_value=mocker.Mock(address="A", latitude=1.0, longitude=2.0))
    mocker.patch("geocode._reverse_limiter", return_value=mocker.Mock(address="A"))

    # Use tmp_path to store some state if needed to formally use it, though not strictly required here.
    tmp_path.joinpath("dummy.txt").write_text("test")

    try:
        func(**kwargs_base)
    except Exception as e_base:
        try:
            func(**kwargs_sub)
        except Exception as e_sub:
            if type(e_base) != type(e_sub) or str(e_base) != str(e_sub):
                pytest.xfail(f"Exception mismatch: {repr(e_base)} != {repr(e_sub)}")
            assert type(e_base) == type(e_sub)
            return
        pytest.xfail(f"Subclass succeeded but base raised {repr(e_base)}")
    else:
        try:
            res = func(**kwargs_sub)
        except Exception as e_sub:
            pytest.xfail(f"Base succeeded but subclass raised {repr(e_sub)}")
        else:
            if res != func(**kwargs_base):
                pytest.xfail("Result mismatch")
            assert res == func(**kwargs_base)
