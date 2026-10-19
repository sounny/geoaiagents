import ast
import glob
import os
import pytest

# Allowlist for files that currently violate the rule.
ALLOWLIST = set()

def get_python_files():
    files = glob.glob("*.py") + glob.glob("plugins/*.py")
    return [f for f in files if os.path.basename(f) not in ALLOWLIST]

@pytest.mark.parametrize("filepath", get_python_files())
def test_no_pass_in_block_with_other_statements(filepath):
    """
    Parses every top-level .py module and plugins/*.py with ast and fails
    when a pass statement appears in a block that has other statements.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source, filename=filepath)

    violations = []
    for node in ast.walk(tree):
        for attr in ['body', 'orelse', 'finalbody']:
            if hasattr(node, attr):
                block = getattr(node, attr)
                if isinstance(block, list) and len(block) > 1:
                    for stmt in block:
                        if isinstance(stmt, ast.Pass):
                            violations.append(f"Line {stmt.lineno}: pass statement found in a block that has other statements.")

    assert not violations, f"File {filepath} has pass statement violations:\n" + "\n".join(violations)
