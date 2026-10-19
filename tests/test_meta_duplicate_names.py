import ast
import glob
import os

ALLOWLIST = set()

def test_no_duplicate_function_or_method_names():
    # Find all top-level .py files and plugins/*.py files
    top_level_files = glob.glob("*.py")
    plugin_files = glob.glob("plugins/*.py")
    files_to_check = top_level_files + plugin_files

    duplicates = []

    for filepath in files_to_check:
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                content = f.read()
                tree = ast.parse(content, filename=filepath)
            except SyntaxError:
                # If there's a syntax error, we skip or it would fail elsewhere.
                # Usually product code won't have syntax errors unless currently broken.
                continue

        # Check module level
        module_funcs = set()
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name in module_funcs:
                    dup_id = f"{filepath}::{node.name}"
                    if dup_id not in ALLOWLIST:
                        duplicates.append(dup_id)
                else:
                    module_funcs.add(node.name)

        # Check class level
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_methods = set()
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if item.name in class_methods:
                            dup_id = f"{filepath}::{node.name}::{item.name}"
                            if dup_id not in ALLOWLIST:
                                duplicates.append(dup_id)
                        else:
                            class_methods.add(item.name)

    assert not duplicates, f"Found duplicate function or method names not in ALLOWLIST: {duplicates}"
