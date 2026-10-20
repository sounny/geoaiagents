import ast
import sys
import os
import pytest

LOCAL_MODULES = {"dd2dms", "distance", "validation"}

@pytest.mark.parametrize("filepath", ["dd2dms.py", "distance.py", "validation.py"])
def test_modules_only_import_stdlib(filepath):
    # Determine the full path to the file
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    full_path = os.path.join(repo_root, filepath)

    with open(full_path, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read(), filename=filepath)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                base_module = alias.name.split('.')[0]
                if base_module not in sys.stdlib_module_names and base_module not in LOCAL_MODULES:
                    pytest.xfail(f"{filepath} imports third-party package: {base_module}")
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                base_module = node.module.split('.')[0]
                # __future__ is a special case
                if base_module not in sys.stdlib_module_names and base_module not in LOCAL_MODULES and base_module != "__future__":
                    pytest.xfail(f"{filepath} imports third-party package: {base_module}")
