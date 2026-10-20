import ast
import glob
import os
import pytest

# Allowlist for files that are allowed to have global statements inside functions
ALLOWLIST = {"webchat.py"}

def test_no_global_statements():
    """
    Parses every top-level .py module and plugins/*.py with ast
    and fails on any "global" statement inside a function,
    with an allowlist for current offenders.
    """
    target_files = glob.glob("*.py") + glob.glob("plugins/*.py")

    offenders = []

    for filepath in target_files:
        basename = os.path.basename(filepath)
        if basename in ALLOWLIST:
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=filepath)
            except SyntaxError:
                # Skip files with syntax errors, let other tests catch those
                continue

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for child in ast.walk(node):
                        if isinstance(child, ast.Global):
                            offenders.append(f"{filepath}: function '{node.name}' uses global {child.names}")

    if offenders:
        pytest.fail("Found 'global' statements inside functions in the following files:\n" + "\n".join(offenders))
