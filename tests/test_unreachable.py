import ast
import glob
import os
import pytest

# Allowed files with known unreachable statements (currently empty as none found).
ALLOWLIST = []

def get_unreachable_code(filepath):
    """
    Parses the file and returns a list of tuples (filepath, lineno, stmt_type)
    for statements that follow a return, raise, break, or continue in the same block.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        # Ignore syntax errors, which should be caught by other tests
        return []

    offenders = []

    for node in ast.walk(tree):
        for attr in ['body', 'orelse', 'finalbody']:
            if hasattr(node, attr):
                block = getattr(node, attr)
                if isinstance(block, list):
                    for i, stmt in enumerate(block):
                        if isinstance(stmt, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
                            if i < len(block) - 1:
                                offenders.append((filepath, stmt.lineno, type(stmt).__name__))

    return offenders

def test_no_unreachable_code_after_control_flow():
    """
    A meta-test that checks all top-level .py modules and plugins/*.py
    to ensure no statements appear after a return, raise, break, or continue
    in the same block.
    """
    # Find all relevant python files
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    py_files = glob.glob(os.path.join(base_dir, "*.py")) + glob.glob(os.path.join(base_dir, "plugins", "*.py"))

    all_offenders = []
    for f in py_files:
        basename = os.path.basename(f)
        if basename in ALLOWLIST:
            continue

        offenders = get_unreachable_code(f)
        all_offenders.extend(offenders)

    if all_offenders:
        error_msg = "Found unreachable statements after return, raise, break, or continue:\n"
        for filepath, lineno, stmt_type in all_offenders:
            error_msg += f"  {os.path.relpath(filepath, base_dir)}:{lineno} (after {stmt_type})\n"
        pytest.fail(error_msg)
