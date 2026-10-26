import ast
import glob
import os
import pytest

ALLOWLIST = [
]

def test_no_keys_in_membership():
    """
    Test that top-level .py modules and plugins/*.py do not contain "x in d.keys()" membership tests.
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
            if isinstance(node, ast.Compare):
                if any(isinstance(op, (ast.In, ast.NotIn)) for op in node.ops):  # codespell:ignore NotIn
                    for comparator in node.comparators:
                        if isinstance(comparator, ast.Call):
                            if isinstance(comparator.func, ast.Attribute) and comparator.func.attr == "keys":
                                offenders.append(f"{basename}:{node.lineno}")

    assert not offenders, f"Found 'x in d.keys()' membership tests in files: {', '.join(offenders)}"
