import ast
import os

# Allowlist for existing test classes that inherit from unittest.TestCase
# Format: {"tests/test_filename.py": {"ClassName1", "ClassName2"}}
ALLOWLIST = {}

def test_no_unittest_testcase():
    """
    Parses every tests/test_*.py file with ast and fails on subclasses of
    unittest.TestCase inside tests/ (prefer plain pytest functions).
    Uses an allowlist for current offenders.
    """
    tests_dir = os.path.abspath(os.path.dirname(__file__))

    offenders = []

    for root, _, files in os.walk(tests_dir):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                path = os.path.join(root, file)
                rel_path = os.path.relpath(path, start=os.path.dirname(tests_dir))

                with open(path, "r", encoding="utf-8") as f:
                    try:
                        tree = ast.parse(f.read(), filename=path)
                    except SyntaxError:
                        continue

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        for base in node.bases:
                            is_testcase = False

                            # Check for unittest.TestCase
                            if isinstance(base, ast.Attribute):
                                if base.attr == "TestCase" and isinstance(base.value, ast.Name) and base.value.id == "unittest":
                                    is_testcase = True
                            # Check for TestCase (if imported directly)
                            elif isinstance(base, ast.Name):
                                if base.id == "TestCase":
                                    is_testcase = True

                            if is_testcase:
                                allowed_classes = ALLOWLIST.get(rel_path.replace("\\", "/"), set())
                                if node.name not in allowed_classes:
                                    offenders.append(f"{rel_path}:{node.lineno} - class {node.name}(unittest.TestCase)")

    assert not offenders, "Found subclasses of unittest.TestCase (prefer plain pytest functions):\n" + "\n".join(offenders)
