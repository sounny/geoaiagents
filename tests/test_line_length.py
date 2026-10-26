import subprocess
import os

ALLOWLIST = {
    "geocode.py",
    "tests/test_file_loaders.py",
    "tests/test_webchat_tables.py",
    'submit.py',
    'tests/test_agents_md.py',
    'tests/test_ast_class_attributes.py',
    'tests/test_ast_lambdas.py',
    'tests/test_ast_subprocess.py',
    'tests/test_chmod_meta.py',
    'tests/test_docstrings.py',
    'tests/test_geocode.py',
    'tests/test_geocode_fallback.py',
    'tests/test_gitleaks_workflow.py',
    'tests/test_imports.py',
    'tests/test_meta_asserts.py',
    'tests/test_meta_bool_compare.py',
    'tests/test_meta_class_method_count.py',
    'tests/test_meta_duplicate_methods.py',
    'tests/test_meta_except_handlers.py',
    'tests/test_meta_exit.py',
    'tests/test_meta_fixture_sleep.py',
    'tests/test_meta_input.py',
    'tests/test_meta_len_comparison.py',
    'tests/test_meta_loops.py',
    'tests/test_meta_magic_numbers.py',
    'tests/test_meta_mktemp.py',
    'tests/test_meta_pass_statement.py',
    'tests/test_meta_print_outside_entry.py',
    'tests/test_meta_secrets.py',
    'tests/test_meta_skip.py',
    'tests/test_meta_skip_reason.py',
    'tests/test_meta_swallowed_exceptions.py',
    'tests/test_meta_tarfile_extraction.py',
    'tests/test_meta_test_bare_return_fixture.py',
    'tests/test_meta_three_arg_getattr.py',
    'tests/test_meta_type_compare.py',
    'tests/test_meta_type_ignore.py',
    'tests/test_meta_unittest_testcase.py',
    'tests/test_meta_verify.py',
    'tests/test_module_docstrings.py',
    'tests/test_os_environ_ast.py',
    'tests/test_raise_not_implemented.py',
    'tests/test_random_seed_meta.py',
    'tests/test_subprocess_ast.py',
    'tests/test_todos.py'
}

def test_line_length_under_120():
    """Ensure no tracked .py file has a line longer than 120 characters, with an allowlist."""
    try:
        # Get all tracked files
        tracked_files = subprocess.check_output(
            ["git", "ls-files"], text=True
        ).splitlines()
    except subprocess.CalledProcessError:
        return

    py_files = [f for f in tracked_files if f.endswith(".py")]

    offenders = []

    for filepath in py_files:
        if filepath in ALLOWLIST:
            continue

        if not os.path.exists(filepath):
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                # Remove trailing newline for length calculation
                line_content = line.rstrip("\r\n")
                if len(line_content) > 120:
                    offenders.append(f"{filepath}:{line_num} ({len(line_content)} chars)")

    if offenders:
        msg = "The following files contain lines longer than 120 characters:\n"
        msg += "\n".join(offenders)
        msg += "\n\nPlease keep lines under 120 characters."
        assert not offenders, msg
