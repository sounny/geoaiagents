import ast
import glob

def test_no_assert_tuple():
    offenders = []
    allowlist = []

    for file_path in glob.glob('tests/test_*.py'):
        if file_path == 'tests/test_meta_assert_tuple.py':
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read(), filename=file_path)
            except SyntaxError:
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Assert):
                if isinstance(node.test, ast.Tuple) and len(node.test.elts) > 0:
                    if file_path not in allowlist:
                        offenders.append(f"{file_path}:{node.lineno}")

    assert not offenders, f"Found assert statements with non-empty tuples (always True): {offenders}"
