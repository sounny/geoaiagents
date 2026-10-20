import ast
import glob
import pytest
from pathlib import Path

# Allowlist for files that currently have this issue (if any)
ALLOWLIST = set()

def test_no_duplicate_test_names_in_test_files():
    """
    Parses all tests/test_*.py files and ensures there are no duplicate test names
    (either top-level functions or methods in a Test* class).
    """
    project_root = Path(__file__).parent.parent
    test_files = glob.glob(str(project_root / "tests" / "test_*.py"))

    offenders = []

    for filename in test_files:
        path = Path(filename)
        if path.name in ALLOWLIST:
            continue

        with path.open("r", encoding="utf-8") as f:
            content = f.read()

        try:
            tree = ast.parse(content)
        except SyntaxError:
            continue # Ignore syntax errors for this test, other tools will catch them

        seen_functions = set()
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith("test_"):
                    if node.name in seen_functions:
                        offenders.append(f"{path.name}: duplicate top-level function '{node.name}'")
                    seen_functions.add(node.name)
            elif isinstance(node, ast.ClassDef):
                if node.name.startswith("Test"):
                    seen_methods = set()
                    for child in node.body:
                        if isinstance(child, ast.FunctionDef):
                            if child.name.startswith("test_"):
                                if child.name in seen_methods:
                                    offenders.append(f"{path.name}: duplicate method '{child.name}' in class '{node.name}'")
                                seen_methods.add(child.name)

    assert not offenders, "Duplicate test names found:\n" + "\n".join(offenders)
