1. **Create `tests/test_llm_utils.py`**:
   - Write `test_call_llm_with_retry_immediate_success` that mocks `client.chat.completions.create` to return a successful `SimpleNamespace(choices=[{'ok': True}])`, asserting it is returned identically and called exactly once (no real network).
   - Write `test_call_llm_with_retry_timeout_then_success` that sets `client.chat.completions.create.side_effect = [TimeoutError('t'), SimpleNamespace(choices=[{'ok': True}])]` to test timeout on the first attempt and success on the second. It will assert the response is the choices response and `create` was called twice, keeping the name distinct from first-attempt success and max_retries failure titles.
2. **Install testing dependencies**: Run `pip install openai pytest pytest-mock pytest-repeat folium gradio geopy` and `bash install_requirements.sh`.
3. **Run tests**: Run `python -m pytest tests/test_llm_utils.py` to ensure the tests pass successfully.
4. **Complete pre-commit steps**: Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
5. **Submit changes**: Submit the code changes.
