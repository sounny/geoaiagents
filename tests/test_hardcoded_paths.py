import ast
import glob
import re
import pytest

def is_hardcoded_path(s):
    if not isinstance(s, str):
        return False
    if s.startswith('/home/') or s.startswith('/Users/') or s.startswith('/tmp/'):
        return True
    if re.match(r'^[a-zA-Z]:[\\/]', s):
        return True
    return False

def test_no_hardcoded_paths():
    files = glob.glob('*.py') + glob.glob('plugins/*.py')

    allowlist = {
        # file_name: set_of_strings
    }

    offenders = []
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        try:
            tree = ast.parse(content, filename=file)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                val = node.value
                if is_hardcoded_path(val):
                    if file in allowlist and val in allowlist[file]:
                        continue
                    offenders.append((file, val))

    assert not offenders, f"Hardcoded absolute paths found: {offenders}"
