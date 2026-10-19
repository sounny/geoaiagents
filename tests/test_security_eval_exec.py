import ast
import glob
import os
import pytest

def test_no_eval_exec_in_codebase():
    """
    Parses every top-level .py module and plugins/*.py with ast
    and fails on any call to the builtins eval() or exec(),
    with an allowlist for current offenders.
    """
    files = glob.glob('*.py') + glob.glob('plugins/*.py')

    # allowlist for current offenders
    allowlist = {} # format: { 'filename.py': ['eval', 'exec'] }

    offenders = []

    for f in files:
        with open(f, 'r', encoding='utf-8') as fp:
            try:
                tree = ast.parse(fp.read(), filename=f)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                        func_name = node.func.id
                        if func_name in ('eval', 'exec'):
                            if f not in allowlist or func_name not in allowlist[f]:
                                offenders.append(f"{f}: found {func_name}() call")
            except SyntaxError:
                # skip files that can't be parsed if any
                pass

    assert not offenders, "Found prohibited eval() or exec() calls:\n" + "\n".join(offenders)
