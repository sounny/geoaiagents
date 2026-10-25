1. Write tests in `tests/test_webchat_all.py` (or similar file in `tests/`) that:
   - Call each public function of `webchat.py` twice: once with positional arguments, once with keyword arguments.
   - Assert that the returned values of both calls are identical (using a normalization helper for `create_map_html` because Folium embeds random hashes, or `ANY` if appropriate).
   - Mock all network/model calls and the filesystem using `mocker` and `tmp_path` to avoid external dependencies.
2. Complete pre commit steps to ensure proper testing, verification, review, and reflection are done.
3. Submit the changes.
