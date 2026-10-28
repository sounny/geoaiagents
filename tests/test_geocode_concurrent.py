import pytest
import concurrent.futures
import time
import json
from unittest.mock import MagicMock
import geocode

@pytest.fixture
def mock_requests_get(mocker):
    mock_get = mocker.patch("requests.Session.get")
    call_count = 0

    def side_effect(url, **kwargs):
        nonlocal call_count
        call_count += 1
        time.sleep(0.01) # encourage thread interleaving

        # Nominatim returns list for geocode, dict for reverse
        if "reverse" in url:
            resp = {
                "place_id": call_count,
                "lat": f"{40.0 + call_count}",
                "lon": f"{-70.0 + call_count}",
                "display_name": f"Mock Address {call_count}",
                "address": {"city": "Mock City"}
            }
        else:
            resp = [{
                "place_id": call_count,
                "lat": f"{40.0 + call_count}",
                "lon": f"{-70.0 + call_count}",
                "display_name": f"Mock Address {call_count}",
                "class": "place",
                "type": "city"
            }]

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = json.dumps(resp)
        mock_resp.json.return_value = resp
        return mock_resp

    mock_get.side_effect = side_effect
    return mock_get


@pytest.mark.parametrize("func, arg", [
    (geocode.parse_locations, "Loc A\nLoc B"),
    pytest.param(geocode.get_coordinates, "Loc A", marks=pytest.mark.xfail(raises=AssertionError, reason="Bug: Cache stampede on concurrent calls evaluates HTTP request multiple times, returning different mock results.")),
    pytest.param(geocode.reverse_geocode_coordinates, "40.0, -70.0", marks=pytest.mark.xfail(raises=AssertionError, reason="Bug: Lack of global thread-safe caching evaluates HTTP request multiple times on concurrent calls, returning different mock results.")),
    pytest.param(geocode.geocode_locations, "Loc A\nLoc B", marks=pytest.mark.xfail(raises=AssertionError, reason="Bug: Cache stampede in underlying get_coordinates evaluates HTTP request multiple times, returning different mock results."))
])
def test_geocode_concurrent_execution(mock_requests_get, func, arg):
    if hasattr(func, "cache_clear"):
        func.cache_clear()

    # Get expected single-threaded result
    expected = func(arg)

    # Clear cache to simulate cold start across threads
    if hasattr(func, "cache_clear"):
        func.cache_clear()

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(func, arg) for _ in range(10)]
        results = [f.result() for f in futures]

    for res in results:
        assert res == expected, f"Threaded result {res} does not match single-threaded result {expected}"
