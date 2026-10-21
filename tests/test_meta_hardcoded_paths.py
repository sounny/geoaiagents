import ast
import glob
import os

def test_meta_no_hardcoded_paths_in_tests():
    files = glob.glob('tests/test_*.py')

    allowlist = {
        'test_hardcoded_paths.py': {'/home/', '/Users/'},
        'test_meta_hardcoded_paths.py': {'/home/', '/Users/', 'C:\\'}
    }

    offenders = []

    for filepath in files:
        filename = os.path.basename(filepath)
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read(), filename=filepath)
            except Exception:
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                val = node.value
                if val.startswith('/home/') or val.startswith('/Users/') or val.startswith('C:\\'):
                    if filename in allowlist and val in allowlist[filename]:
                        continue
                    offenders.append(f"{filepath}: {val}")

    assert not offenders, f"Hardcoded paths found in tests:\n" + "\n".join(offenders)
