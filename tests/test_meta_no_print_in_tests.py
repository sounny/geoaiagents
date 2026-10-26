import ast
import glob

# Allowlist for existing test files that currently contain print() calls in test functions.
# New files or new violations in existing files outside this list will fail the meta-test.
ALLOWLIST = [
    "tests/test_star_imports.py"
]

def test_no_print_in_test_functions():
    """
    Ensure no print() calls are present inside test functions (i.e. functions starting with 'test_').
    Prefer using standard pytest assertions or the caplog fixture instead.
    """
    offenders = []

    # Iterate over all test files
    for file_path in glob.glob('tests/test_*.py'):
        if file_path in ALLOWLIST:
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        try:
            tree = ast.parse(content, filename=file_path)
        except SyntaxError:
            continue  # Skip files with syntax errors (they'll fail other tests anyway)

        # Walk through the AST to find function definitions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                # For each test function, look for Call nodes that are print()
                for child in ast.walk(node):
                    if isinstance(child, ast.Call) and isinstance(child.func, ast.Name) and child.func.id == 'print':
                        offenders.append(f"{file_path}::{node.name}")
                        # We only need to record one offense per function to avoid noise
                        break

    if offenders:
        msg = "Found print() calls inside the following test functions. Please use assertions or caplog instead:\n"
        msg += "\n".join(f"  - {offender}" for offender in offenders)
        assert not offenders, msg
