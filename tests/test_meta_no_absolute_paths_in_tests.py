import ast
import glob
import re
import pytest

def test_no_absolute_paths_in_tests():
    """
    Ensures that test files do not contain string literals starting with
    /home/, /Users/, or a Windows drive letter.
    """
    pattern = re.compile(r'^(/home/|/Users/|[a-zA-Z]:[\\/])')

    allowlist = {
        'tests/test_hardcoded_paths.py'
    }

    offenders = []

    for filepath in glob.glob('tests/test_*.py'):
        if filepath in allowlist:
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read(), filename=filepath)
            except SyntaxError:
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if pattern.match(node.value):
                    offenders.append(f"{filepath}:{node.lineno}")

    assert not offenders, f"Found hardcoded absolute paths in tests: {', '.join(offenders)}"
