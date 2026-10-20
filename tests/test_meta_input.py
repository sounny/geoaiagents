import ast
import glob
import os
import pytest

ALLOWLIST = {
    "dd2dms.py",
    "distance.py",
    "geoai_cli.py",
    "geocode.py",
    "humboldt.py",
}

def is_main_guard(node):
    # check if node is `if __name__ == '__main__':`
    if isinstance(node, ast.If):
        if isinstance(node.test, ast.Compare):
            if isinstance(node.test.left, ast.Name) and node.test.left.id == '__name__':
                if len(node.test.ops) == 1 and isinstance(node.test.ops[0], ast.Eq):
                    if len(node.test.comparators) == 1:
                        comp = node.test.comparators[0]
                        if isinstance(comp, ast.Constant) and comp.value == '__main__':
                            return True
    return False

def check_file_for_invalid_input_calls(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read(), filename=filepath)

    # We need to find all input() calls and verify their parents
    # AST doesn't have parent links by default, so we add them
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node

    violations = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == 'input':
                # Check if it's within a __main__ guard or a CLI entry function (like main)
                current = node
                is_valid = False
                while hasattr(current, 'parent'):
                    current = current.parent
                    if isinstance(current, ast.FunctionDef) and current.name in ('main', 'repl', '_read_value_or_stdin'):
                        # Allowing typical CLI entry point names.
                        is_valid = True
                        break
                    if is_main_guard(current):
                        is_valid = True
                        break

                if not is_valid:
                    violations.append(node.lineno)

    return violations

def test_no_input_calls_outside_main_or_cli():
    # Find all top-level .py files and plugins/*.py
    files = glob.glob('*.py') + glob.glob('plugins/*.py')

    errors = []

    for filepath in files:
        basename = os.path.basename(filepath)
        violations = check_file_for_invalid_input_calls(filepath)

        if violations:
            if basename not in ALLOWLIST:
                errors.append(f"{filepath}: input() calls at lines {violations}")

    if errors:
        pytest.fail("Found input() calls outside __main__ guard or CLI entry function:\n" + "\n".join(errors))
