import ast
import glob
import pytest

# Allowlist for existing offenders (file_path:line_number)
ALLOWLIST = set()

def get_python_files():
    """Return a list of all top-level .py files and .py files in plugins/."""
    return glob.glob('*.py') + glob.glob('plugins/*.py')

@pytest.mark.parametrize("filepath", get_python_files())
def test_no_walrus_in_comprehensions(filepath):
    """
    Test that no top-level .py module or plugin contains a list/set/dict
    comprehension or generator expression with an assignment expression (walrus)
    used only for side effects (i.e. where the comprehension itself is used as a statement).
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
        except SyntaxError:
            pytest.skip(f"SyntaxError in {filepath}")

    offenders = []

    for node in ast.walk(tree):
        # We look for comprehensions used only for side effects.
        # This typically means they are the value of an Expr statement.
        if isinstance(node, ast.Expr):
            if isinstance(node.value, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                # Check if this comprehension contains a NamedExpr (walrus)
                has_walrus = any(isinstance(child, ast.NamedExpr) for child in ast.walk(node.value))
                if has_walrus:
                    identifier = f"{filepath}:{node.lineno}"
                    if identifier not in ALLOWLIST:
                        offenders.append(identifier)

    assert not offenders, f"Found comprehensions with walrus used for side effects: {offenders}"
