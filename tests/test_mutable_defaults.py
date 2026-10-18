import ast
import glob
import os

ALLOWLIST = []

def test_no_mutable_defaults():
    files = [f for f in glob.glob("*.py") if not f.startswith("test_")] + glob.glob("plugins/*.py")
    offenders = []

    for filepath in files:
        with open(filepath, "r", encoding="utf-8") as file:
            try:
                tree = ast.parse(file.read(), filename=filepath)
            except SyntaxError:
                continue

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                defaults = getattr(node.args, "defaults", []) + getattr(node.args, "kw_defaults", [])
                for default in defaults:
                    if default is None:
                        continue
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        func_identifier = f"{filepath}::{node.name}"
                        if func_identifier not in ALLOWLIST:
                            offenders.append(func_identifier)

    assert not offenders, f"Found mutable default arguments in functions: {offenders}"
