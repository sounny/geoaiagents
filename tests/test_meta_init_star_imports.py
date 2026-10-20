import ast
import glob
import os

def test_no_star_imports_in_init():
    """
    Test that no __init__.py files use 'from X import *'.
    Includes an allowlist for current offenders.
    """
    allowlist = []

    files_to_check = glob.glob("*.py") + glob.glob("plugins/*.py")
    offenders = []

    for file_path in files_to_check:
        if os.path.basename(file_path) != "__init__.py":
            continue

        if file_path in allowlist:
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=file_path)
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if any(alias.name == "*" for alias in node.names):
                    offenders.append(f"{file_path}:{node.lineno}")

    assert not offenders, "Found 'from X import *' in the following __init__.py files:\n" + "\n".join(offenders)
