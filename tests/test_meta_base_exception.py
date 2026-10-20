import ast
import glob
import itertools
import pytest

# Allowlist for files that currently violate the rule.
# (Empty for now, as no offenders were found)
ALLOWLIST = set()

def is_reraise(node):
    """
    Checks if there is an ast.Raise node within the subtree of `node`.
    """
    for sub in ast.walk(node):
        if isinstance(sub, ast.Raise):
            return True
    return False

def test_meta_no_unreraised_base_exception():
    """
    Meta-test to parse every top-level .py module and plugins/*.py using ast
    and fail on except BaseException handlers that do not re-raise.
    """
    files = list(itertools.chain(glob.glob("*.py"), glob.glob("plugins/*.py")))

    violations = []

    for filepath in files:
        if filepath in ALLOWLIST:
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()

        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue  # Skip files with syntax errors

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                is_base_exception = False

                # Check if it's 'except BaseException:'
                if node.type is not None:
                    if isinstance(node.type, ast.Name):
                        if node.type.id == "BaseException":
                            is_base_exception = True
                    elif isinstance(node.type, ast.Tuple):
                        for elt in node.type.elts:
                            if isinstance(elt, ast.Name) and elt.id == "BaseException":
                                is_base_exception = True

                if is_base_exception:
                    if not is_reraise(node):
                        violations.append(f"{filepath}:{node.lineno}")

    assert not violations, "Found except BaseException handlers that do not re-raise:\n" + "\n".join(violations)
