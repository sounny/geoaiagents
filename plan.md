1. **Add `test_geocode_get_coordinates_parameters` in `tests/test_geocode.py`:**
   - Mock all HTTP calls (`get_json`, `get_text`) to `geocode._geolocator.adapter` and `time.sleep` (because RateLimiter will wait).
   - Call `geocode.get_coordinates.cache_clear()` prior to each test to clear the cache.
   - Test omitting optional parameters (`timeout`, `bounding_box`, `language`), passing them explicitly as defaults, and passing the main argument by keyword (`location_query`).
2. **Add `test_geocode_reverse_geocode_coordinates_parameters` in `tests/test_geocode.py`:**
   - Mock all HTTP calls and `time.sleep`.
   - Test `geocode.reverse_geocode_coordinates` omitting optional parameters (`timeout`, `language`), passing them as defaults, and passing the main argument by keyword (`coordinates_str`).
3. **Add `test_geocode_parse_locations_parameters` in `tests/test_geocode.py`:**
   - Test `geocode.parse_locations` by passing the main argument by keyword (`locations_str`). This function has no optional parameters, but we'll cover keyword vs positional for the single arg.
4. **Add `test_geocode_geocode_locations_parameters` in `tests/test_geocode.py`:**
   - Mock HTTP calls and `time.sleep`.
   - Test `geocode.geocode_locations` by passing the main argument by keyword (`locations_str`). Cover `get_coordinates` cache clear logic here too.
5. **Add `test_geocode_main_parameters` in `tests/test_geocode.py`:**
   - Mock HTTP calls, `builtins.input`, `sys.argv`, and `time.sleep`.
   - The user asked to call *each public function or constructor*. We will verify if we can call `geocode.main()` with parameters... actually `main` doesn't take parameters. But we can test calling it. We will test running `main` but ensure all paths mock out network dependencies (especially `call_llm_with_retry`).
6. **Pre-commit checks**
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
