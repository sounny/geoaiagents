import ast
import glob
import pytest

def get_complexity(node):
    complexity = 0
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler, ast.With, ast.AsyncWith)):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
        elif isinstance(child, ast.comprehension):
            complexity += 1 + len(child.ifs)
    return complexity

def test_cyclomatic_complexity():
    allowlist = {
        "humboldt.py::main": 20,
        "file_loaders.py::load_geojson": 17
    }

    files_to_check = glob.glob("*.py") + glob.glob("plugins/*.py")
    offenders = []

    for file_path in files_to_check:
        if file_path.startswith("test_") or file_path == "test_meta_complexity.py":
            continue

        with open(file_path, "r", encoding="utf-8") as file:
            try:
                tree = ast.parse(file.read())
            except SyntaxError:
                continue

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                c = get_complexity(node)
                func_id = f"{file_path}::{node.name}"

                # Use allowlist value if present, else limit is 15
                limit = allowlist.get(func_id, 15)

                if c > limit:
                    offenders.append(f"{func_id} has complexity {c} (limit: {limit})")

    if offenders:
        pytest.fail("Functions with cyclomatic complexity > 15 found:\n" + "\n".join(offenders))
