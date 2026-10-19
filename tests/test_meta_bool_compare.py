import ast
import glob
import pytest

ALLOWLIST = [
    # Add files here if they currently violate the rule and shouldn't fail the test
]

def is_bool_constant(node):
    """Check if an AST node is a boolean constant (True or False)."""
    if isinstance(node, ast.Constant) and type(node.value) is bool:
        return True
    # For Python < 3.8 compatibility
    if hasattr(ast, 'NameConstant') and getattr(node, 'value', None) in (True, False) and type(getattr(node, 'value', None)) is bool:
        return True
    return False

def test_no_bool_literal_comparisons():
    """
    Ensure top-level modules and plugins do not compare to True or False using == or !=.
    They should use 'is' or 'is not' (or check truthiness directly).
    """
    files = glob.glob('*.py') + glob.glob('plugins/*.py')

    offenders = []

    for filepath in files:
        if filepath in ALLOWLIST:
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read(), filename=filepath)
            except Exception:
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Compare):
                for op, comp in zip(node.ops, node.comparators):
                    if isinstance(op, (ast.Eq, ast.NotEq)):
                        if is_bool_constant(node.left) or is_bool_constant(comp):
                            lineno = getattr(node, 'lineno', '?')
                            offenders.append(f"{filepath}:{lineno}")

    if offenders:
        pytest.fail(
            f"Found == or != comparison with boolean literal (True/False) in files: "
            f"{', '.join(offenders)}. Use 'is' or 'is not' for booleans, or check truthiness directly."
        )
