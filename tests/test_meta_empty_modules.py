import ast
import glob

ALLOWLIST = [
]

def test_meta_no_empty_modules():
    """
    AST-based meta-test that parses every top-level .py module and plugins/*.py
    (excluding __init__.py files) and fails if the total count of files containing
    no statements grows beyond the current count.
    """
    files = glob.glob("*.py") + glob.glob("plugins/*.py")
    files = [f for f in files if not f.endswith("__init__.py")]

    empty_modules = []

    for filename in files:
        with open(filename, "r", encoding="utf-8") as f:
            source = f.read()

        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue

        if len(tree.body) == 0:
            if filename not in ALLOWLIST and filename != "test_meta_empty_modules.py":
                empty_modules.append(filename)

    assert len(empty_modules) == 0, f"Found new empty modules: {empty_modules}"
