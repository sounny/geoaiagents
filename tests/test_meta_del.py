import ast
import glob
import pytest
from pathlib import Path

# Allowlist for files that are allowed to have classes defining __del__
# e.g. "humboldt.py", "plugins/example_plugin.py"
ALLOWLIST = set()

def get_python_files():
    top_level = glob.glob("*.py")
    plugins = glob.glob("plugins/*.py")
    return top_level + plugins

@pytest.mark.parametrize("filepath", get_python_files())
def test_no_del_in_classes(filepath):
    # Skip files in the allowlist
    if filepath in ALLOWLIST:
        return

    path = Path(filepath)
    if not path.is_file():
        return

    content = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(content, filename=filepath)
    except SyntaxError:
        pytest.fail(f"Could not parse {filepath}")

    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__del__":
                    offenders.append(node.name)

    if offenders:
        pytest.fail(f"File {filepath} defines __del__ in classes: {', '.join(offenders)}. "
                    f"If this is intentional, add the file to the ALLOWLIST in tests/test_meta_del.py.")
