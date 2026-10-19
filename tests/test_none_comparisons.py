import ast
import glob
import os
import pytest

# Expected format: {'filename.py': [line_number, ...]}
ALLOWLIST = {}

def get_python_files():
    # Only parsing top-level .py modules and plugins/*.py
    files = glob.glob('*.py') + glob.glob('plugins/*.py')
    # Filter out generated files, testing scripts, or virtual envs
    return sorted([f for f in files if os.path.isfile(f)])

@pytest.mark.parametrize("filepath", get_python_files())
def test_no_none_comparisons(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
        except SyntaxError:
            pytest.fail(f"SyntaxError while parsing {filepath}")

    offenses = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            # Check left operand (e.g. None == x)
            if isinstance(node.left, ast.Constant) and node.left.value is None:
                if node.ops and isinstance(node.ops[0], (ast.Eq, ast.NotEq)):
                    offenses.append(node.lineno)

            # Check comparators (e.g. x == None)
            for op, comp in zip(node.ops, node.comparators):
                if isinstance(op, (ast.Eq, ast.NotEq)):
                    if isinstance(comp, ast.Constant) and comp.value is None:
                        offenses.append(node.lineno)

    allowed_offenses = ALLOWLIST.get(filepath, [])
    unallowed_offenses = sorted(list(set(line for line in offenses if line not in allowed_offenses)))

    assert not unallowed_offenses, (
        f"Found comparison to None using == or != in {filepath} on lines {unallowed_offenses}. "
        "Use 'is None' or 'is not None' instead."
    )
