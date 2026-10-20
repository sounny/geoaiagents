import ast
import glob
import os
import pytest

ALLOWLIST = [
]

def test_no_mixed_chained_comparisons():
    """
    Test that top-level .py modules and plugins/*.py do not contain chained comparisons
    that mix is/in with < or > such as a < b is c.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = glob.glob(os.path.join(project_root, "*.py")) + glob.glob(os.path.join(project_root, "plugins", "*.py"))

    offenders = []

    for filepath in files:
        basename = os.path.basename(filepath)
        if basename in ALLOWLIST:
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        try:
            tree = ast.parse(content, filename=filepath)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Compare) and len(node.ops) > 1:
                has_is_in = any(isinstance(op, (ast.Is, ast.IsNot, ast.In, ast.NotIn)) for op in node.ops)
                has_ineq = any(isinstance(op, (ast.Lt, ast.LtE, ast.Gt, ast.GtE)) for op in node.ops)
                if has_is_in and has_ineq:
                    offenders.append(f"{basename}:{node.lineno}")

    assert not offenders, f"Found chained comparisons mixing is/in with < or > in files: {', '.join(offenders)}"
