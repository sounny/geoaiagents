import ast
import glob
import os
import pytest

# Allowlist for files that are allowed to have global statements inside functions
ALLOWLIST = {"webchat.py": 1}


def test_no_global_statements():
    """
    Parses every top-level .py module and plugins/*.py with ast
    and counts "global" statements inside functions. Fails if the
    total grows beyond the current count in the allowlist.
    """
    target_files = glob.glob("*.py") + glob.glob("plugins/*.py")

    offenders = []

    for filepath in target_files:
        basename = os.path.basename(filepath)
        allowed_count = ALLOWLIST.get(basename, 0)
        file_offenders = 0

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
                            file_offenders += 1

        if file_offenders > allowed_count:
            if allowed_count == 0:
                offenders.append(
                    f"{filepath} has {file_offenders} global statements, which exceeds the limit of 0."
                )
            else:
                offenders.append(
                    f"{filepath} has {file_offenders} global statements, which exceeds its allowlisted baseline of {allowed_count}."
                )

    if offenders:
        pytest.fail(
            "Files with too many global statements found:\n" + "\n".join(offenders)
        )
