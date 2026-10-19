import ast
import glob
import os
import pytest

ALLOWLIST = {
    "distance.py": {"Sequence"}
}

def find_unused_imports(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read(), filename=filepath)

    imported_names = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname if alias.asname else alias.name.split('.')[0]
                imported_names[name] = alias.name
        elif isinstance(node, ast.ImportFrom):
            if node.module == '__future__':
                continue
            if node.names[0].name == '*':
                continue
            for alias in node.names:
                name = alias.asname if alias.asname else alias.name
                imported_names[name] = alias.name

    used_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            if isinstance(node.ctx, (ast.Load, ast.Del)):
                used_names.add(node.id)
        # Check __all__
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == '__all__':
                    if isinstance(node.value, (ast.List, ast.Tuple, ast.Set)):
                        for elt in node.value.elts:
                            if hasattr(elt, 'value') and isinstance(elt.value, str):
                                used_names.add(elt.value)
                            elif hasattr(elt, 's'):
                                used_names.add(elt.s)

    unused = []
    is_init = os.path.basename(filepath) == '__init__.py'

    for name, orig in imported_names.items():
        if name not in used_names:
            if not is_init:
                unused.append(name)

    return unused

def test_no_unused_imports():
    files = [f for f in glob.glob("*.py") + glob.glob("plugins/*.py") if os.path.isfile(f)]

    errors = []
    for filepath in files:
        filename = os.path.basename(filepath)
        unused = find_unused_imports(filepath)

        allowed_for_file = ALLOWLIST.get(filename, set())

        for name in unused:
            if name not in allowed_for_file:
                errors.append(f"{filepath} imports '{name}' but it is never used")

    if errors:
        pytest.fail("\n".join(errors))
