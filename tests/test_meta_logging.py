import ast
import glob
import os
import pytest

ALLOWED_OFFENDERS = [
    "webchat.py"
]

def test_no_invalid_getlogger():
    files = glob.glob("*.py") + glob.glob("plugins/*.py")
    violations = []

    for file_path in files:
        if os.path.basename(file_path) in ALLOWED_OFFENDERS or file_path in ALLOWED_OFFENDERS:
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=file_path)
            except SyntaxError:
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr == "getLogger":
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "logging":
                        is_valid = False
                        if len(node.args) == 1:
                            arg = node.args[0]
                            if isinstance(arg, ast.Name) and arg.id == "__name__":
                                is_valid = True
                        if not is_valid:
                            violations.append(f"{file_path}:{getattr(node, 'lineno', '?')}")

    if violations:
        pytest.fail(f"Found logging.getLogger() called with something other than __name__:\n" + "\n".join(violations))
