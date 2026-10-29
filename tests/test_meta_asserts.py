import ast
import glob

def test_no_asserts_in_test_functions():
    offenders = []

    for filename in glob.glob('tests/test_*.py'):
        if filename == 'tests/test_meta_asserts.py':
            continue

        with open(filename, 'r') as f:
            tree = ast.parse(f.read(), filename=filename)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                has_assert = False
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.Assert):
                        has_assert = True
                        break
                    if isinstance(subnode, ast.Call):
                        # Check for pytest.raises or pytest.warns
                        if isinstance(subnode.func, ast.Attribute) and isinstance(subnode.func.value, ast.Name) and subnode.func.value.id == 'pytest':
                            if subnode.func.attr in ('raises', 'warns', 'fail', 'skip', 'xfail', 'fail', 'skip', 'xfail'):
                                has_assert = True
                                break
                        # Check for mock assert_* calls
                        if isinstance(subnode.func, ast.Attribute) and subnode.func.attr.startswith('assert_'):
                            has_assert = True
                            break

                if not has_assert:
                    offenders.append(f"{filename}::{node.name}")

    # Allowlist for existing offenders
    allowlist = [
        'tests/test_plugins_init.py::test_plugins_package_imports_cleanly',
        'tests/test_example_plugin.py::test_unknown_hook_safe'
    ]

    missing_from_allowlist = [o for o in offenders if o not in allowlist]
    assert not missing_from_allowlist, f"Test functions without asserts found (not in allowlist): {missing_from_allowlist}"
