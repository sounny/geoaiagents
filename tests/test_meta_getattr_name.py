import ast
import glob
import pytest
from pathlib import Path

# Allowlist for files that currently use getattr(..., "name")
ALLOWLIST = {
    # If any current offenders exist, add them here
}

def get_python_files():
    top_level = glob.glob("*.py")
    plugins = glob.glob("plugins/*.py")
    return top_level + plugins

@pytest.mark.parametrize("filepath", get_python_files())
def test_meta_no_getattr_name(filepath):
    """
    Meta-test to parse every top-level .py module and plugins/*.py using ast
    and fail on getattr(obj, "name") calls with a constant string and no default (use obj.name).
    """
    if filepath in ALLOWLIST:
        return

    path = Path(filepath)
    if not path.is_file():
        return

    try:
        content = path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=filepath)
    except Exception:
        # If there's a syntax error, we ignore it for this meta-test
        # as it is checked by other tests
        return

    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == 'getattr':
                if len(node.args) == 2 and not node.keywords:
                    arg1 = node.args[1]
                    # Check for Constant "name" (Python 3.8+)
                    if isinstance(arg1, ast.Constant) and isinstance(arg1.value, str) and arg1.value == "name":
                        offenders.append(node.lineno)
                    # Check for Str "name" (Python 3.7-)
                    elif isinstance(arg1, ast.Str) and arg1.s == "name":
                        offenders.append(node.lineno)

    if offenders:
        lines = ", ".join(map(str, offenders))
        pytest.fail(f"File {filepath} uses getattr(obj, 'name') without default at line(s): {lines}. "
                    f"Use obj.name instead. If this is intentional, add the file to the ALLOWLIST "
                    f"in tests/test_meta_getattr_name.py.")
