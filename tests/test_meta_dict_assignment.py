import ast
import glob
import os
import pytest

# Allowlist for known offenders. Format: {"filename.py": [line_number_1, line_number_2]}
ALLOWLIST = {}

def get_python_files():
    """Get all top-level .py files and .py files in plugins/ directory."""
    top_level_files = glob.glob("*.py")
    plugin_files = glob.glob("plugins/*.py")
    return top_level_files + plugin_files

def check_dict_assignments(filepath):
    """Check a file for assignments to obj.__dict__[xyz] and obj.__dict__.update()."""
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    offenses = []
    for node in ast.walk(tree):
        # Check for obj.__dict__[xyz] = ...
        if isinstance(node, ast.Subscript):
            if isinstance(node.value, ast.Attribute) and node.value.attr == '__dict__':
                if isinstance(node.ctx, ast.Store):
                    offenses.append(node.lineno)

        # Check for obj.__dict__.update(...)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == 'update':
                if isinstance(node.func.value, ast.Attribute) and node.func.value.attr == '__dict__':
                    offenses.append(node.lineno)

    return offenses

@pytest.mark.parametrize("filepath", get_python_files())
def test_no_dict_assignments(filepath):
    """Meta-test to ensure no unallowed assignments to __dict__ exist."""
    offenses = check_dict_assignments(filepath)
    allowed_lines = ALLOWLIST.get(os.path.basename(filepath), [])

    unallowed_offenses = [line for line in offenses if line not in allowed_lines]

    assert not unallowed_offenses, (
        f"File '{filepath}' contains disallowed assignments to __dict__ or "
        f"__dict__.update() at lines: {unallowed_offenses}. "
        f"If this is intentional, add it to the ALLOWLIST in tests/test_meta_dict_assignment.py."
    )
