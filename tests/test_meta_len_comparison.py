import ast
import glob
import os
import pytest

# Allowlist for existing offenders of the rule: len(x) == 0, len(x) > 0, etc.
# Format: { "filename": [line_number_1, line_number_2, ...] }
ALLOWLIST = {}

def get_python_files():
    root_dir = os.path.dirname(os.path.dirname(__file__))
    files = glob.glob(os.path.join(root_dir, '*.py')) + glob.glob(os.path.join(root_dir, 'plugins', '*.py'))
    return [f for f in files if os.path.isfile(f)]

def test_no_len_comparison_to_zero():
    errors = []

    for filepath in get_python_files():
        filename = os.path.relpath(filepath, start=os.path.dirname(os.path.dirname(__file__)))

        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read(), filename=filepath)
            except SyntaxError:
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Compare):
                left = node.left
                for op, right in zip(node.ops, node.comparators):
                    is_len_to_zero = False

                    if isinstance(left, ast.Call) and isinstance(left.func, ast.Name) and left.func.id == 'len' and isinstance(right, ast.Constant) and right.value == 0:
                        is_len_to_zero = True
                    elif isinstance(left, ast.Constant) and left.value == 0 and isinstance(right, ast.Call) and isinstance(right.func, ast.Name) and right.func.id == 'len':
                        is_len_to_zero = True

                    if is_len_to_zero:
                        if filename not in ALLOWLIST or node.lineno not in ALLOWLIST[filename]:
                            errors.append(f"{filename}:{node.lineno} compares len() to 0")
                    left = right

    assert not errors, "Found len() comparisons to 0 (which is an anti-pattern, use `if x:` or `if not x:`):\n" + "\n".join(errors)
