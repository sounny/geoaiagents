import ast
import glob

def test_no_assert_true():
    """
    Ensure that test files do not contain 'assert True' or 'assertTrue(True)'.
    """
    offenders = []

    for filename in glob.glob('tests/test_*.py'):
        if filename == 'tests/test_meta_assert_true.py':
            continue

        with open(filename, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read(), filename=filename)
            except SyntaxError:
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Assert):
                # Check for assert True
                if isinstance(node.test, ast.Constant) and node.test.value is True:
                    offenders.append(filename)
                elif type(node.test).__name__ == 'NameConstant' and getattr(node.test, 'value', None) is True:
                    offenders.append(filename)
            elif isinstance(node, ast.Call):
                # Check for assertTrue(True)
                is_assert_true = False
                if isinstance(node.func, ast.Attribute) and node.func.attr == 'assertTrue':
                    is_assert_true = True
                elif isinstance(node.func, ast.Name) and node.func.id == 'assertTrue':
                    is_assert_true = True

                if is_assert_true and node.args:
                    arg = node.args[0]
                    if isinstance(arg, ast.Constant) and arg.value is True:
                        offenders.append(filename)
                    elif type(arg).__name__ == 'NameConstant' and getattr(arg, 'value', None) is True:
                        offenders.append(filename)

    # Remove duplicates
    offenders = list(set(offenders))

    # Allowlist for existing offenders
    allowlist = []

    missing_from_allowlist = [o for o in offenders if o not in allowlist]
    assert not missing_from_allowlist, f"Files with 'assert True' or 'assertTrue(True)' found (not in allowlist): {sorted(missing_from_allowlist)}"
