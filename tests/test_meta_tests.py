import ast
import glob
import pytest

def test_all_test_files_have_tests():
    test_files = glob.glob("tests/test_*.py")
    for file in test_files:
        with open(file, "r") as f:
            tree = ast.parse(f.read())

        has_test = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                has_test = True
                break
            if isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
                has_test = True
                break

        assert has_test, f"{file} defines no test function or Test class"
