1. **Append a test for argument parsing idempotency**
   - In `tests/test_geoai_cli.py`, add `test_arg_parsing_twice` testing that calling `parser.parse_args` twice with the same inputs returns identical outputs.
   - Note that default values like `os.getenv` in `_build_parser` are evaluated at definition/build time, not parse time, so they are not time-dependent during parsing.
2. **Append a test for main function idempotency**
   - In `tests/test_geoai_cli.py`, add `test_main_twice` testing that calling `main()` twice with identical arguments returns identical return code, stdout, and stderr.
   - Mock external dependencies like `tool_registry.create_registry` and `openai.OpenAI`.
   - Mock `builtins.input` with side effects for chat commands to ensure tests do not hang.
3. **Run the full test suite**
   - Ensure `~/.local/share/pipx/venvs/pytest/bin/python -m pytest` passes for the entire suite.
4. **Complete pre-commit steps**
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
5. **Submit changes**
   - Call the `submit` tool to finish the task.
