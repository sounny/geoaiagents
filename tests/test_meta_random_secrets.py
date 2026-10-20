import ast
import glob
from pathlib import Path
import pytest

# Allowlist for existing offenders: (filename, variable_name)
ALLOWLIST = set([
])

def is_random_call(node):
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == 'random':
                if node.func.attr in ('random', 'randint', 'choice'):
                    return True
        elif isinstance(node.func, ast.Name):
            if node.func.id in ('random', 'randint', 'choice'):
                return True
    return False

def get_python_files():
    # Top-level .py files
    top_level = glob.glob("*.py")
    # plugins/*.py files
    plugins = glob.glob("plugins/*.py")
    return sorted(list(set(top_level + plugins)))

@pytest.mark.parametrize("filepath", get_python_files())
def test_no_random_secrets(filepath):
    path = Path(filepath)
    if not path.is_file():
        pytest.skip(f"{filepath} is not a file")

    try:
        content = path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=filepath)
    except Exception as e:
        pytest.fail(f"Failed to parse {filepath}: {e}")

    errors = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if is_random_call(node.value):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name = target.id.lower()
                        if any(kw in name for kw in ['token', 'secret', 'password', 'key']):
                            if (filepath, target.id) not in ALLOWLIST:
                                errors.append(f"Line {node.lineno}: '{target.id}' assigned using random.*")
        elif isinstance(node, ast.AnnAssign):
            if node.value and is_random_call(node.value):
                if isinstance(node.target, ast.Name):
                    name = node.target.id.lower()
                    if any(kw in name for kw in ['token', 'secret', 'password', 'key']):
                        if (filepath, node.target.id) not in ALLOWLIST:
                            errors.append(f"Line {node.lineno}: '{node.target.id}' assigned using random.*")

    if errors:
        pytest.fail(f"Found unsafe random assignments in {filepath}:\n" + "\n".join(errors))
