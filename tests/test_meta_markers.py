import ast
import glob
import os
import pytest

# Allowlist for current offenders: {"filename.py": ["test_function_name"]}
ALLOWLIST = {}

def test_pytest_markers_have_reasons():
    """
    Scans tests/*.py and fails if any pytest.mark.skip, skipif, or xfail
    marker lacks a reason= argument.
    """
    offenders = []

    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_files = glob.glob(os.path.join(test_dir, "*.py"))

    for filepath in test_files:
        filename = os.path.basename(filepath)

        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()

        try:
            tree = ast.parse(source, filename=filepath)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                for dec in node.decorator_list:
                    is_marker = False
                    has_reason = False
                    marker_name = ""

                    # Check for uncalled markers like @pytest.mark.skip
                    if isinstance(dec, ast.Attribute):
                        if (isinstance(dec.value, ast.Attribute) and
                            getattr(dec.value.value, "id", "") == "pytest" and
                            dec.value.attr == "mark"):
                            if dec.attr in ("skip", "skipif", "xfail"):
                                is_marker = True
                                marker_name = dec.attr
                                has_reason = False

                    # Check for called markers like @pytest.mark.skip(...)
                    elif isinstance(dec, ast.Call):
                        func = dec.func
                        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Attribute):
                            if (getattr(func.value.value, "id", "") == "pytest" and
                                func.value.attr == "mark"):
                                if func.attr in ("skip", "skipif", "xfail"):
                                    is_marker = True
                                    marker_name = func.attr
                                    for kw in dec.keywords:
                                        if kw.arg == "reason":
                                            has_reason = True
                                            break

                    if is_marker and not has_reason:
                        if filename in ALLOWLIST and node.name in ALLOWLIST[filename]:
                            continue
                        offenders.append(f"{filename}::{node.name} has @pytest.mark.{marker_name} without a reason=")

    if offenders:
        pytest.fail("Found pytest markers without a reason argument:\n" + "\n".join(offenders))
