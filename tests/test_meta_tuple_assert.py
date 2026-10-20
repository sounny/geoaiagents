import ast
import glob
from pathlib import Path

# Allowlist for existing offenders (filename -> list of line numbers)
# e.g., {"tests/test_something.py": [42]}
ALLOWLIST = {}

def get_python_files():
    files = glob.glob("*.py") + glob.glob("plugins/*.py")
    return [Path(f) for f in files]

def test_no_tuple_asserts():
    offenders = []

    for file_path in get_python_files():
        filename = str(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                content = f.read()
                tree = ast.parse(content, filename=filename)
            except SyntaxError:
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Assert):
                if isinstance(node.test, ast.Tuple) and len(node.test.elts) > 0:
                    if filename not in ALLOWLIST or node.lineno not in ALLOWLIST[filename]:
                        offenders.append(f"{filename}:{node.lineno}")

    assert not offenders, "Found assert statements with tuple literals:\n" + "\n".join(offenders)
