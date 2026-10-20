import ast
import os
import pytest

# There are no existing offenders for missing reason in pytest.mark.xfail in tests/
ALLOWLIST = []

def has_reason_arg(node: ast.Call) -> bool:
    """Check if a pytest.xfail or @pytest.mark.xfail call has a reason."""
    # Check kwargs first
    for kw in node.keywords:
        if kw.arg == "reason":
            return True

    # Check positional args based on what function is being called
    # If it's pytest.xfail, it only takes one positional argument `reason`
    is_pytest_xfail = isinstance(node.func, ast.Attribute) and node.func.attr == "xfail" and isinstance(node.func.value, ast.Name) and node.func.value.id == "pytest"

    if is_pytest_xfail:
        if node.args:
            return True

    # If it's @pytest.mark.xfail, the first positional argument is the condition, the second is the reason.
    is_pytest_mark_xfail = isinstance(node.func, ast.Attribute) and node.func.attr == "xfail" and isinstance(node.func.value, ast.Attribute) and node.func.value.attr == "mark" and isinstance(node.func.value.value, ast.Name) and node.func.value.value.id == "pytest"

    if is_pytest_mark_xfail:
        if len(node.args) >= 2:
            return True

    return False

def test_meta_no_xfails_without_reason():
    """Ensure that all pytest.xfail() and @pytest.mark.xfail calls have a reason."""
    offenders = []

    # Find all test files recursively
    test_files = []
    for root, _, files in os.walk("tests"):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                test_files.append(os.path.join(root, file))

    for filename in test_files:
        with open(filename, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=filename)
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                # Check for pytest.xfail() or pytest.mark.xfail() inside pytest.param
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute) and node.func.attr == "xfail":
                        # pytest.xfail()
                        if isinstance(node.func.value, ast.Name) and node.func.value.id == "pytest":
                            if not has_reason_arg(node):
                                offender = f"{filename}:{node.lineno}"
                                if offender not in ALLOWLIST:
                                    offenders.append(offender)
                        # pytest.mark.xfail()
                        elif isinstance(node.func.value, ast.Attribute) and node.func.value.attr == "mark":
                            if isinstance(node.func.value.value, ast.Name) and node.func.value.value.id == "pytest":
                                if not has_reason_arg(node):
                                    offender = f"{filename}:{node.lineno}"
                                    if offender not in ALLOWLIST:
                                        offenders.append(offender)

                # Check for @pytest.mark.xfail (no parens) as a decorator
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    for dec in node.decorator_list:
                        # @pytest.mark.xfail (no parens)
                        if isinstance(dec, ast.Attribute) and dec.attr == "xfail":
                            if isinstance(dec.value, ast.Attribute) and dec.value.attr == "mark":
                                if isinstance(dec.value.value, ast.Name) and dec.value.value.id == "pytest":
                                    offender = f"{filename}:{dec.lineno}"
                                    if offender not in ALLOWLIST:
                                        offenders.append(offender)

    if offenders:
        pytest.fail(f"Found pytest.xfail() or @pytest.mark.xfail calls without a reason:\n" + "\n".join(offenders))
