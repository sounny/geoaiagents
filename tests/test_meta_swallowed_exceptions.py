import ast
import glob
import os

ALLOWLIST = ["webchat.py"]

def test_no_swallowed_exceptions():
    """
    Test that top-level .py modules and plugins/*.py do not have except handlers
    that silently swallow errors (e.g. only contain `pass` or `...`).
    """
    files = glob.glob('*.py') + glob.glob('plugins/*.py')
    offenders = []

    for filepath in files:
        basename = os.path.basename(filepath)
        if basename in ALLOWLIST:
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read(), filename=filepath)
            except SyntaxError:
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if len(node.body) == 1:
                    stmt = node.body[0]
                    if isinstance(stmt, ast.Pass):
                        offenders.append(f"{filepath}:{stmt.lineno}")
                    elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and stmt.value.value is Ellipsis:
                        offenders.append(f"{filepath}:{stmt.lineno}")

    assert not offenders, f"Found exceptions that are silently swallowed: {', '.join(offenders)}"
