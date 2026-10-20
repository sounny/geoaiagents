import ast
import glob
import os
import pytest

ALLOWLIST = []

def has_reason_arg(node: ast.Call) -> bool:
    """Check if a pytest.skip or @pytest.mark.skip call has a reason."""
    # Check positional args (e.g. pytest.skip("reason"))
    # We just check if there is at least one argument,
    # to allow variables, f-strings, constants etc.
    if node.args:
        return True

    # Check kwargs (e.g. pytest.skip(reason="reason"))
    for kw in node.keywords:
        if kw.arg == "reason":
            return True

    return False

def test_meta_no_skips_without_reason():
    """Ensure that all pytest.skip() and @pytest.mark.skip calls have a reason."""
    offenders = []

    # Find all test files
    test_files = glob.glob("tests/test_*.py")

    for filename in test_files:
        with open(filename, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=filename)
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                # Check for pytest.skip()
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute) and node.func.attr == "skip":
                        if isinstance(node.func.value, ast.Name) and node.func.value.id == "pytest":
                            if not has_reason_arg(node):
                                offender = f"{filename}:{node.lineno}"
                                if offender not in ALLOWLIST:
                                    offenders.append(offender)

                # Check for @pytest.mark.skip or @pytest.mark.skip()
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    for dec in node.decorator_list:
                        # @pytest.mark.skip (no parens)
                        if isinstance(dec, ast.Attribute) and dec.attr == "skip":
                            if isinstance(dec.value, ast.Attribute) and dec.value.attr == "mark":
                                if isinstance(dec.value.value, ast.Name) and dec.value.value.id == "pytest":
                                    offender = f"{filename}:{dec.lineno}"
                                    if offender not in ALLOWLIST:
                                        offenders.append(offender)

                        # @pytest.mark.skip() (with parens)
                        elif isinstance(dec, ast.Call):
                            if isinstance(dec.func, ast.Attribute) and dec.func.attr == "skip":
                                if isinstance(dec.func.value, ast.Attribute) and dec.func.value.attr == "mark":
                                    if isinstance(dec.func.value.value, ast.Name) and dec.func.value.value.id == "pytest":
                                        if not has_reason_arg(dec):
                                            offender = f"{filename}:{dec.lineno}"
                                            if offender not in ALLOWLIST:
                                                offenders.append(offender)

    if offenders:
        pytest.fail(f"Found pytest.skip() or @pytest.mark.skip calls without a reason:\n" + "\n".join(offenders))
