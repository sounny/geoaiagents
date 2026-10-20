import ast
import glob
import os
import pytest

# Allowlist can be specified as a list of "filename:lineno" strings, e.g. ["install_requirements.py:42"]
ALLOWLIST = []

def test_no_verify_false_in_calls():
    # Gather top-level .py files and plugins/*.py
    files = glob.glob('*.py') + glob.glob('plugins/*.py')

    offenders = []

    for filename in files:
        # Skip this test file itself or any other tests if they happen to match
        if filename.startswith('tests/') or filename.startswith('test_'):
            continue

        with open(filename, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read(), filename=filename)
            except SyntaxError:
                # If there's a syntax error, we ignore it for this meta-test
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                for kw in node.keywords:
                    if kw.arg == 'verify':
                        # Check if the value is False
                        is_false = False
                        if isinstance(kw.value, ast.Constant):
                            if kw.value.value is False:
                                is_false = True
                        elif hasattr(ast, 'NameConstant') and isinstance(kw.value, getattr(ast, 'NameConstant')): # For older Python versions
                            if kw.value.value is False:
                                is_false = True

                        if is_false:
                            lineno = getattr(node, 'lineno', '?')
                            identifier = f"{filename}:{lineno}"
                            if identifier not in ALLOWLIST:
                                offenders.append(identifier)

    if offenders:
        pytest.fail(f"Found function calls with verify=False not in allowlist:\n" + "\n".join(offenders))
