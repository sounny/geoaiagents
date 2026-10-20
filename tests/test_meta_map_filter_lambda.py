import ast
import glob
import os
import pytest

def get_python_files():
    # Top-level .py files
    files = glob.glob("*.py")
    # plugins/*.py
    files.extend(glob.glob("plugins/*.py"))
    return sorted([f for f in files if os.path.isfile(f)])

ALLOWLIST = {
    # 'filename.py': count
}

@pytest.mark.parametrize("filepath", get_python_files())
def test_no_map_filter_lambda(filepath):
    """
    Ensure that we don't introduce new map/filter calls whose first argument is a lambda.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
        except SyntaxError:
            pytest.skip(f"SyntaxError when parsing {filepath}")

    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in ("map", "filter"):
                if node.args and isinstance(node.args[0], ast.Lambda):
                    count += 1

    allowed = ALLOWLIST.get(filepath, 0)
    assert count <= allowed, (
        f"File {filepath} contains {count} map/filter calls with a lambda as the first argument "
        f"(allowed: {allowed}). Please use list comprehensions or generator expressions instead."
    )
