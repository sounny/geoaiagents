1. **Understand `create_map_html` differing output**:
   `folium.Map` and other components generate HTML that contains random UUIDs (like `map_7f39402a515906f488e6`) so that multiple maps on the same page do not collide. Thus, `create_map_html` is not purely referentially transparent if we expect identical strings. We can still test it concurrently, but we can't assert the output string exactly matches. Wait, the prompt says "assert every result matches the single-threaded result, using xfail with a short note where behavior looks like a bug". Since the UUIDs change every time, it fails the exact string match. We should mark `create_map_html` with `xfail` and note "folium generates random map IDs".

2. **Add a new test file `tests/test_webchat_concurrent.py` or modify `tests/test_webchat.py`**:
   The prompt says "tests/test_webchat.py" in "Add tests for pytest tests for webchat.py (mock any network or model calls) that call pure public functions from several threads at once via concurrent.futures and assert every result matches the single-threaded result...". I will append it to `tests/test_webchat.py`.

3. **Plan for pytest test**:
   ```python
   import pytest
   import concurrent.futures
   from webchat import infer_location, create_map_html, parse_table_coordinates, parse_distance_table, extract_map_coords

   def run_concurrently(func, *args, max_workers=10, iterations=50):
       expected = func(*args)
       with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
           futures = [executor.submit(func, *args) for _ in range(iterations)]
           for f in concurrent.futures.as_completed(futures):
               assert f.result() == expected

   def test_infer_location_concurrent():
       run_concurrently(infer_location, "show me a map for New York")

   @pytest.mark.xfail(reason="folium generates random map IDs on each call, so results differ")
   def test_create_map_html_concurrent():
       run_concurrently(create_map_html, [(48.8, 2.3), (51.5, -0.1)])

   def test_parse_table_coordinates_concurrent():
       run_concurrently(parse_table_coordinates, "| Lat | Lon |\n|---|---|\n| 48.8 | 2.3 |\n", 0, 1)

   def test_parse_distance_table_concurrent():
       run_concurrently(parse_distance_table, "| Lat1 | Lon1 | Lat2 | Lon2 |\n|---|---|---|---|\n| 48.8 | 2.3 | 51.5 | -0.1 |")

   def test_extract_map_coords_concurrent():
       run_concurrently(extract_map_coords, "distance", "| Lat1 | Lon1 | Lat2 | Lon2 |\n|---|---|---|---|\n| 48.8 | 2.3 | 51.5 | -0.1 |")
   ```

4. **Verify the plan**:
   We will submit this plan for review.
