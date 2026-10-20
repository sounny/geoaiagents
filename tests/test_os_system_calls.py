import ast
import glob
import os
import pytest

ALLOWLIST = []

def test_no_os_system_or_popen():
    # Find all top-level .py files
    root_files = glob.glob("*.py")

    # Find all .py files in plugins/
    plugin_files = glob.glob("plugins/*.py")

    all_files = root_files + plugin_files

    offending_calls = []

    for filepath in all_files:
        if filepath in ALLOWLIST:
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=filepath)
            except SyntaxError:
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for os.system or os.popen
                # They appear as ast.Attribute inside ast.Call
                if isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "os":
                        if node.func.attr in ("system", "popen"):
                            offending_calls.append(f"{filepath}:{node.lineno}: os.{node.func.attr}() called")

    if offending_calls:
        pytest.fail("Found os.system() or os.popen() calls:\n" + "\n".join(offending_calls))
