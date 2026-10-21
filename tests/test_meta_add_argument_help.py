import ast
import glob
import os
import pytest

ALLOWLIST = set()

def check_file_for_add_argument_help(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
        except Exception:
            return []

    violations = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            is_add_argument = False
            if isinstance(node.func, ast.Attribute) and node.func.attr == 'add_argument':
                is_add_argument = True
            elif isinstance(node.func, ast.Name) and node.func.id == 'add_argument':
                is_add_argument = True

            if is_add_argument:
                has_help = False
                for kw in node.keywords:
                    if kw.arg == 'help':
                        has_help = True
                        break

                if not has_help:
                    violations.append(node.lineno)

    return violations

def test_add_argument_has_help():
    files = glob.glob('*.py') + glob.glob('plugins/*.py')

    errors = []

    for filepath in files:
        basename = os.path.basename(filepath)
        violations = check_file_for_add_argument_help(filepath)

        if violations:
            if filepath not in ALLOWLIST and basename not in ALLOWLIST:
                errors.append(f"{filepath}: add_argument() calls missing 'help=' keyword at lines {violations}")

    if errors:
        pytest.fail("Found add_argument() calls without 'help=' keyword argument:\n" + "\n".join(errors))
