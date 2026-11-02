1. Write tests in `tests/test_webchat.py` for `infer_location`, `parse_table_coordinates`, `parse_distance_table`, `extract_map_coords`, `respond`, and `chat` in `webchat.py`.
2. Define custom `MyStr(str)` and `MyDict(dict)` classes in the test file.
3. Pass `MyStr` and `MyDict` to these public functions.
4. Mock network and model calls (like `call_llm_with_retry`, `folium.Map`, `OpenAI`).
5. Assert current results or errors.
6. Use `@pytest.mark.xfail` with a short note where the behavior looks like a bug.
7. Skip if none take strings or dicts.
8. Complete pre commit steps to ensure proper testing, verification, review, and reflection are done.
9. Submit the code.
