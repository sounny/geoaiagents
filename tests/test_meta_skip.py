import ast
import os
import pytest

# Allowlist for existing offenders
ALLOWLIST = [
    "test_geocode.py:29"
]

def test_no_reasonless_skips():
    issues = []
    tests_dir = os.path.dirname(__file__)
    for filename in os.listdir(tests_dir):
        if not (filename.startswith("test_") and filename.endswith(".py")):
            continue

        file_path = os.path.join(tests_dir, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=file_path)
            except SyntaxError:
                continue

        for node in ast.walk(tree):
            # Check pytest.skip()
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                if node.func.value.id == "pytest" and node.func.attr == "skip":
                    has_reason = any(k.arg == "reason" for k in node.keywords)
                    if not has_reason and len(node.args) == 0:
                        issues.append(f"{filename}:{node.lineno}")
                    elif not has_reason and len(node.args) > 0 and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                        # pytest.skip("reason") is fine
                        pass

            # Check @pytest.mark.skip and @pytest.mark.skipif
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.ClassDef):
                for dec in node.decorator_list:
                    # @pytest.mark.skip (without parens)
                    if isinstance(dec, ast.Attribute) and isinstance(dec.value, ast.Attribute) and isinstance(dec.value.value, ast.Name):
                        if dec.value.value.id == "pytest" and dec.value.attr == "mark" and dec.attr in ("skip", "skipif"):
                            issues.append(f"{filename}:{dec.lineno}")
                    # @pytest.mark.skip() or @pytest.mark.skipif()
                    elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute) and isinstance(dec.func.value, ast.Attribute) and isinstance(dec.func.value.value, ast.Name):
                        if dec.func.value.value.id == "pytest" and dec.func.value.attr == "mark" and dec.func.attr in ("skip", "skipif"):
                            has_reason = any(k.arg == "reason" for k in dec.keywords)
                            if dec.func.attr == "skip":
                                has_positional_reason = len(dec.args) > 0 and isinstance(dec.args[0], ast.Constant) and isinstance(dec.args[0].value, str)
                                if not has_reason and not has_positional_reason:
                                    issues.append(f"{filename}:{dec.lineno}")
                            elif dec.func.attr == "skipif":
                                if not has_reason:
                                    issues.append(f"{filename}:{dec.lineno}")

    # Filter out allowlist
    new_issues = [issue for issue in issues if issue not in ALLOWLIST]

    if new_issues:
        pytest.fail("Found pytest.skip / pytest.mark.skip / pytest.mark.skipif usages without a reason:\n" + "\n".join(new_issues))
