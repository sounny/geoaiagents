import ast
import os
import glob
import pytest

ALLOWLIST = [
    # Format: "tests/test_filename.py::fixture_name"
]

def test_no_sleep_in_fixtures():
    offenders = []
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    for filepath in glob.glob(os.path.join(tests_dir, "test_*.py")):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        try:
            tree = ast.parse(content, filename=filepath)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                is_fixture = False
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Name) and dec.id == "fixture":
                        is_fixture = True
                    elif isinstance(dec, ast.Attribute) and dec.attr == "fixture" and getattr(dec.value, "id", "") == "pytest":
                        is_fixture = True
                    elif isinstance(dec, ast.Call):
                        if isinstance(dec.func, ast.Name) and dec.func.id == "fixture":
                            is_fixture = True
                        elif isinstance(dec.func, ast.Attribute) and dec.func.attr == "fixture" and getattr(dec.func.value, "id", "") == "pytest":
                            is_fixture = True

                if is_fixture:
                    for subnode in ast.walk(node):
                        if isinstance(subnode, ast.Call):
                            is_sleep = False
                            if isinstance(subnode.func, ast.Attribute) and subnode.func.attr == "sleep" and getattr(subnode.func.value, "id", "") == "time":
                                is_sleep = True
                            elif isinstance(subnode.func, ast.Name) and subnode.func.id == "sleep":
                                # Catch potential `from time import sleep` as a best-effort
                                is_sleep = True

                            if is_sleep:
                                rel_path = os.path.relpath(filepath, tests_dir)
                                file_id = f"tests/{rel_path}"
                                offenders.append(f"{file_id}::{node.name}")

    new_offenders = [o for o in offenders if o not in ALLOWLIST]

    assert not new_offenders, f"Found time.sleep() calls in pytest fixture functions: {new_offenders}"
