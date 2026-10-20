import ast
import glob
import pytest
from pathlib import Path

def test_no_string_literal_exprs_outside_docstrings():
    """
    Parses every top-level .py module and plugins/*.py with ast and counts
    expression statements that are only a string literal and are not a docstring.
    Fails if the total grows beyond the current count, with an allowlist for current offenders.
    """
    files_to_check = glob.glob("*.py") + glob.glob("plugins/*.py")

    allowlist = {
        "dd2dms.py": 1
    }

    total_offenders = 0
    details = []

    for filepath in files_to_check:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        try:
            tree = ast.parse(source, filename=filepath)
        except SyntaxError:
            continue

        docstrings = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.body and isinstance(node.body[0], ast.Expr):
                    val = node.body[0].value
                    if isinstance(val, ast.Constant) and isinstance(val.value, str):
                        docstrings.add(node.body[0])
                    elif hasattr(ast, 'Str') and isinstance(val, getattr(ast, 'Str')):
                        docstrings.add(node.body[0])

        file_offenders = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Expr) and node not in docstrings:
                val = node.value
                is_string_literal = False
                if isinstance(val, ast.Constant) and isinstance(val.value, str):
                    is_string_literal = True
                elif hasattr(ast, 'Str') and isinstance(val, getattr(ast, 'Str')):
                    is_string_literal = True

                if is_string_literal:
                    file_offenders += 1
                    details.append(f"{filepath}:{node.lineno}")

        total_offenders += file_offenders

        allowed = allowlist.get(filepath, 0)
        if file_offenders > allowed:
            pytest.fail(f"File {filepath} has {file_offenders} bare string expression(s) not serving as a docstring. Allowed: {allowed}.")

    expected_total = sum(allowlist.values())
    assert total_offenders <= expected_total, (
        f"Total count of bare string expressions ({total_offenders}) exceeded allowlist limit ({expected_total}).\n"
        f"Details:\n" + "\n".join(details)
    )
