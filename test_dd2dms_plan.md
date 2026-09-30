1. **Add test for invalid input in `tests/test_dd2dms.py`**:
   - Create a test function named `test_convert_dd_to_dms_invalid_input`.
   - Call `convert_dd_to_dms('91,0')`.
   - Assert `'_Skipped invalid inputs:_' in result`.
   - Assert ``'`91,0`' in result``.
   - Assert that no data rows are in the table (e.g., checking that the only lines with `|` are the two header lines).
2. **Run tests**:
   - Run `pytest tests/test_dd2dms.py` to ensure the new test passes and no regressions are introduced.
3. **Complete pre commit steps**:
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
