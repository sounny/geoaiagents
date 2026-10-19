import ast
import glob
import pytest

def test_no_not_in_expressions_in_top_level_modules():
    files_to_check = glob.glob('*.py') + glob.glob('plugins/*.py')
    offenders = set()
    allowlist = set() # Add files to allowlist if necessary

    for file_path in files_to_check:
        if file_path in allowlist:
            continue
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content, filename=file_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
                    if isinstance(node.operand, ast.Compare):
                        if len(node.operand.ops) == 1 and isinstance(node.operand.ops[0], ast.In):
                            offenders.add(file_path)
        except Exception as e:
            pytest.fail(f"Error parsing {file_path}: {e}")

    assert not offenders, f"Modules use 'not x in y' instead of 'x not in y': {offenders}"
