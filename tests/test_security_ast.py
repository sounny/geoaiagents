import ast
import glob
import os

ALLOWLIST = []

def get_python_files():
    # Top-level .py files
    files = glob.glob('*.py')
    # plugins/*.py files
    files.extend(glob.glob('plugins/*.py'))
    return [f for f in files if f not in ALLOWLIST]

def check_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()

    tree = ast.parse(source, filename=filepath)
    errors = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                module_name = node.func.value.id
                func_name = node.func.attr

                # Check for yaml.load without SafeLoader
                if module_name == 'yaml' and func_name == 'load':
                    has_safe_loader = False

                    # Check positional arguments
                    if len(node.args) >= 2:
                        arg1 = node.args[1]
                        if isinstance(arg1, ast.Name) and arg1.id == 'SafeLoader':
                            has_safe_loader = True
                        elif isinstance(arg1, ast.Attribute) and arg1.attr == 'SafeLoader':
                            has_safe_loader = True

                    # Check keyword arguments
                    for kw in node.keywords:
                        if kw.arg == 'Loader':
                            if isinstance(kw.value, ast.Name) and kw.value.id == 'SafeLoader':
                                has_safe_loader = True
                            elif isinstance(kw.value, ast.Attribute) and kw.value.attr == 'SafeLoader':
                                has_safe_loader = True

                    if not has_safe_loader:
                        errors.append(f"Line {node.lineno}: yaml.load() call without SafeLoader")

                # Check for pickle.load or pickle.loads
                elif module_name == 'pickle' and func_name in ('load', 'loads'):
                    errors.append(f"Line {node.lineno}: pickle.{func_name}() call is not allowed")

    return errors

def test_no_unsafe_deserialization():
    python_files = get_python_files()
    all_errors = []

    for filepath in python_files:
        if not os.path.isfile(filepath):
            continue
        errors = check_file(filepath)
        if errors:
            all_errors.append(f"In {filepath}:\n" + "\n".join(errors))

    if all_errors:
        import pytest
        pytest.fail("Found unsafe deserialization calls:\n" + "\n".join(all_errors))
