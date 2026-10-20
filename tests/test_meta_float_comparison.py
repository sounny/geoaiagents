import ast
import glob
from pathlib import Path

# Allowlist for existing offenders:
# Format: { "filename.py": [lineno1, lineno2] }
# Currently we found 0 existing offenders.
ALLOWLIST = {}

def get_files():
    # Only top-level .py and plugins/*.py
    files = glob.glob('*.py') + glob.glob('plugins/*.py')
    # Exclude tests and other non-product code if necessary,
    # but the instructions say "parses every top-level .py module and plugins/*.py".
    # We should exclude test files themselves if they are top-level or just
    # the ones inside `tests/` depending on the exact wording,
    # but "every top-level .py module" implies all of them.
    # Usually we exclude tests themselves from AST meta tests.
    return [f for f in files if not f.startswith('test_')]

def test_no_float_equality_comparisons():
    offenders = []

    for filepath in get_files():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content, filename=filepath)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Compare):
                # node.ops contains the comparison operators (e.g. ==, !=)
                # node.left is the left operand
                # node.comparators contains the right operands
                operands = [node.left] + node.comparators

                for i, op in enumerate(node.ops):
                    if isinstance(op, (ast.Eq, ast.NotEq)):
                        left_operand = operands[i]
                        right_operand = operands[i+1]

                        # Check if either operand is a float constant
                        if (isinstance(left_operand, ast.Constant) and isinstance(left_operand.value, float)) or \
                           (isinstance(right_operand, ast.Constant) and isinstance(right_operand.value, float)):
                            offenders.append((filepath, getattr(node, 'lineno', 0)))

    new_offenders = []
    for filepath, lineno in offenders:
        if filepath in ALLOWLIST and lineno in ALLOWLIST[filepath]:
            continue
        new_offenders.append((filepath, lineno))

    assert len(new_offenders) == 0, (
        "Found float comparisons (== or !=) with a float literal. "
        "Comparing floats directly is error-prone due to precision issues.\n"
        f"Offenders: {new_offenders}"
    )
