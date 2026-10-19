import ast
import glob
import os
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Files allowed to contain assert statements in production code
ALLOWLIST = []

def test_no_asserts_in_production_code():
    """
    Ensures that no assert statements are used in top-level modules or plugins.
    Asserts vanish when python is run with -O, so they shouldn't be used for
    runtime validation in production code.
    """
    files_to_check = []

    # Top-level .py files
    for f in glob.glob(os.path.join(ROOT_DIR, '*.py')):
        basename = os.path.basename(f)
        if not basename.startswith('test_') and basename not in ['conftest.py', 'setup.py']:
            files_to_check.append(f)

    # plugins/*.py files
    for f in glob.glob(os.path.join(ROOT_DIR, 'plugins', '*.py')):
        if not os.path.basename(f).startswith('test_'):
            files_to_check.append(f)

    offenders = []

    for f in files_to_check:
        rel_path = os.path.relpath(f, ROOT_DIR)

        if rel_path in ALLOWLIST:
            continue

        with open(f, 'r', encoding='utf-8') as file:
            try:
                tree = ast.parse(file.read(), filename=f)
            except SyntaxError:
                # If we can't parse it, skip it (other tests should catch syntax errors)
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Assert):
                offenders.append(f"{rel_path}:{node.lineno}")

    if offenders:
        pytest.fail(
            "Found assert statements in non-test code (asserts disappear with python -O):\n" +
            "\n".join(offenders)
        )
