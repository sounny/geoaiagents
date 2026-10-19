import ast
import glob
import os
import re
import pytest

# Allowlist for existing functions that violate snake_case convention.
# Format: {"filename.py": {"FunctionName1", "functionName2"}}
# Currently there are no offenders in the codebase, so the allowlist is empty.
ALLOWLIST = {
}

def is_snake_case(name: str) -> bool:
    """Check if a string is snake_case."""
    return re.match(r"^[a-z_][a-z0-9_]*$", name) is not None

def is_dunder(name: str) -> bool:
    """Check if a method name is a dunder method."""
    return name.startswith("__") and name.endswith("__")

def get_python_files() -> list:
    """Get all top-level .py modules and plugins/*.py."""
    top_level = glob.glob("*.py")
    plugins = glob.glob(os.path.join("plugins", "*.py"))
    return top_level + plugins

def check_file_for_snake_case_functions(filepath: str) -> list:
    """Parse a python file with ast and return a list of function names that are not snake_case."""
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        return [] # Skip files with syntax errors

    violations = []

    # We want to check function names and method names inside classes.
    # ast.FunctionDef and ast.AsyncFunctionDef cover both functions and methods.
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            name = node.name
            if is_dunder(name):
                continue
            if not is_snake_case(name):
                violations.append(name)

    return violations

def test_snake_case_function_names():
    python_files = get_python_files()
    all_violations = {}

    for filepath in python_files:
        violations = check_file_for_snake_case_functions(filepath)
        filename = os.path.basename(filepath)

        # Filter against allowlist
        allowed_for_file = ALLOWLIST.get(filename, set())
        unallowed_violations = [v for v in violations if v not in allowed_for_file]

        if unallowed_violations:
            all_violations[filepath] = unallowed_violations

    if all_violations:
        error_msg = "The following files contain function/method names that are not snake_case:\n"
        for filepath, funcs in all_violations.items():
            error_msg += f"- {filepath}: {', '.join(funcs)}\n"
        error_msg += "\nPlease use snake_case for function and method names."
        pytest.fail(error_msg)
