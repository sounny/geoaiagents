import ast
import glob
from pathlib import Path

def test_no_print_in_tests():
    """Ensure that print() calls in tests do not grow beyond the current baseline."""
    test_files = glob.glob('tests/test_*.py')

    # Allowlist of existing offenders
    # format: {'filename.py': number_of_prints}
    allowlist = {}

    total_allowed = sum(allowlist.values())
    current_offenders = []
    total_found = 0

    for filepath_str in test_files:
        filepath = Path(filepath_str)
        if not filepath.is_file():
            continue

        filename = filepath.name

        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                # If there's a syntax error, we let standard pytest handle it elsewhere
                continue

        file_prints = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'print':
                file_prints += 1

        total_found += file_prints
        if file_prints > 0:
            current_offenders.append((filename, file_prints))

    assert total_found <= total_allowed, (
        f"Found {total_found} print() calls in test files, which exceeds the allowed baseline of {total_allowed}.\n"
        f"Current offenders: {current_offenders}\n"
        "Please use proper assertions or caplog instead of print() in tests."
    )
