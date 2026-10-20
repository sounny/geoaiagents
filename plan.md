1. **Create the meta-test:**
   - I will create a new file `tests/test_meta_if_nesting.py`.
   - The meta-test will use Python's `ast` module to parse all top-level `.py` modules and plugins (`plugins/*.py`).
   - It will contain an AST visitor class that traverses the code and counts nested `if` statements. An `if` statement is considered nested if it appears within another `if` statement's body or `orelse` block. The test requires failing if any `if` statements are nested more than four levels deep.
   - I will use an allowlist for current offenders based on the findings from exploring the codebase (e.g., `file_loaders.py`).
   - If a file not in the allowlist violates this rule, or if an allowlisted file increases its violation count, the test will fail.

2. **Run the test suite:**
   - Execute the test suite using `pytest` to ensure the new meta-test passes and doesn't break existing tests.

3. **Pre-commit step:**
   - I will call `pre_commit_instructions` and follow its instructions to ensure proper testing, verification, review, and reflection are done.

4. **Submit:**
   - I will commit the changes and use the `submit` tool to create a pull request with the new test.
