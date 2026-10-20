import ast
import glob
import pytest

def is_literal(node):
    if isinstance(node, ast.Constant):
        # Exclude booleans since they subclass int in Python but are valid for 'is'
        if isinstance(node.value, bool):
            return False
        if isinstance(node.value, (str, bytes, int, float)):
            return True
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        return is_literal(node.operand)
    # For python versions before 3.8
    if isinstance(node, (ast.Str, ast.Bytes, ast.Num)):
        return True
    return False

def check_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read(), filename=filepath)

    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            left = node.left
            for op, comparator in zip(node.ops, node.comparators):
                if isinstance(op, (ast.Is, ast.IsNot)):
                    # Check if the comparator or the left side is a literal
                    if is_literal(comparator) or is_literal(left):
                        offenders.append(node.lineno)
                left = comparator
    return offenders

def test_no_is_literal_comparisons():
    # Only check top-level .py modules and plugins/*.py
    files = glob.glob("*.py") + glob.glob("plugins/*.py")
    all_offenders = {}

    # Allowlist of existing offenders
    allowlist = {
        # 'filename.py': [line_numbers]
    }

    for f in files:
        res = check_file(f)
        filtered_res = [line for line in res if line not in allowlist.get(f, [])]
        if filtered_res:
            all_offenders[f] = filtered_res

    assert not all_offenders, f"Found 'is' / 'is not' comparisons with literals: {all_offenders}"
