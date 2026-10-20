import ast
import glob
import os
import pytest

ALLOWLIST = [
    # Add files here if there are current offenders
]

def test_no_os_chmod_777_666():
    """
    Top-level Python modules and plugins (plugins/*.py) must not contain os.chmod calls
    whose mode is 0o777 or 0o666.
    """
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    py_files = glob.glob(os.path.join(repo_root, "*.py"))
    plugin_files = glob.glob(os.path.join(repo_root, "plugins", "*.py"))

    files = py_files + plugin_files
    offenders = []

    for filepath in files:
        rel_path = os.path.relpath(filepath, repo_root)
        if rel_path in ALLOWLIST:
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=filepath)
            except SyntaxError:
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and getattr(node.func.value, 'id', None) == 'os' and node.func.attr == 'chmod':
                    # Look for modes 0o777 or 0o666 in args
                    for arg in node.args:
                        if isinstance(arg, ast.Constant) and arg.value in (0o777, 0o666):
                            offenders.append(f"{rel_path}:{node.lineno}")

                    # Look for modes in keywords
                    for kw in node.keywords:
                        if kw.arg == 'mode' and isinstance(kw.value, ast.Constant) and kw.value.value in (0o777, 0o666):
                            offenders.append(f"{rel_path}:{node.lineno}")

    assert not offenders, f"Found os.chmod with 0o777 or 0o666 in: {', '.join(offenders)}"
