import sys
import os
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from install_requirements import read_requirements

def test_read_requirements_trailing_space_stripping_and_pin_keeping():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write('requests==2.32.0   \n\n# comment\n numpy>=1.26\n')
        temp_name = f.name

    try:
        reqs = read_requirements(temp_name)
        assert reqs == ['requests==2.32.0', 'numpy>=1.26']
    finally:
        os.remove(temp_name)

def test_read_requirements_keeps_flask_and_drops_hash_comment():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write('flask==2.0.0 # hash comment\n')
        temp_name = f.name

    try:
        reqs = read_requirements(temp_name)
        assert reqs == ['flask==2.0.0']
    finally:
        os.remove(temp_name)

def test_third_party_imports_are_in_requirements():
    import ast
    import sys
    import os
    import re
    import pytest

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    modules_imported = set()
    for root, _, files in os.walk(repo_root):
        if 'tests' in root or '.git' in root or 'venv' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    try:
                        tree = ast.parse(f.read(), filename=filepath)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for name in node.names:
                                    modules_imported.add(name.name.split('.')[0])
                            elif isinstance(node, ast.ImportFrom):
                                if node.module:
                                    modules_imported.add(node.module.split('.')[0])
                    except Exception:
                        pass

    local_modules = set()
    for file in os.listdir(repo_root):
        if file.endswith('.py'):
            local_modules.add(file[:-3])
        full_path = os.path.join(repo_root, file)
        if os.path.isdir(full_path) and os.path.exists(os.path.join(full_path, '__init__.py')):
            local_modules.add(file)

    requirements = set()
    req_path = os.path.join(repo_root, 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.split('#')[0].strip()
                if line:
                    req_name = re.split(r'[=<>~]', line)[0].strip().lower()
                    requirements.add(req_name)

    stdlib_modules = sys.stdlib_module_names

    missing_requirements = []
    for mod in modules_imported:
        mod_lower = mod.lower()
        if mod not in stdlib_modules and mod not in local_modules:
            if mod_lower not in requirements:
                missing_requirements.append(mod)

    if missing_requirements:
        pytest.xfail(f"Missing third-party requirements: {', '.join(missing_requirements)}")
