1. Verify that `geoai_cli.py` has no public functions that take bytes or string arguments (the only public function is `main`, which takes no arguments, and the rest are private helper functions `_build_parser`, `_read_value_or_stdin`, `_tool_args_for`, `_run_tool_command`, `_run_chat_mode`).
2. Add a skipped test `test_bytes_str_args_skip` to `tests/test_geoai_cli.py` specifying that no public functions take text or bytes.
3. Run the pytest suite using the current active environment to verify the new test runs without issues.
4. Complete pre commit steps to ensure proper testing, verification, review, and reflection are done.
5. Call the `submit` tool to push changes.
