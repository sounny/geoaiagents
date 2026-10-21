import ast
import glob
import os
import pytest

ALLOWLIST = set()
BASELINE_COUNT = 0

def test_meta_raise_generic():
    files = glob.glob('*.py') + glob.glob('plugins/*.py')
    count = 0
    offenders = []

    for filepath in files:
        if filepath in ALLOWLIST:
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read(), filename=filepath)
            except SyntaxError:
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Raise):
                if isinstance(node.exc, ast.Call):
                    if isinstance(node.exc.func, ast.Name):
                        if node.exc.func.id in ('Exception', 'BaseException'):
                            count += 1
                            offenders.append(f"{filepath}:{node.lineno}")
                elif isinstance(node.exc, ast.Name):
                    if node.exc.id in ('Exception', 'BaseException'):
                        count += 1
                        offenders.append(f"{filepath}:{node.lineno}")

    assert count <= BASELINE_COUNT, f"Total raise Exception(...) and raise BaseException(...) count grew to {count}, expected <= {BASELINE_COUNT}. Offenders: {', '.join(offenders)}"
