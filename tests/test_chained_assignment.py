import ast
import glob
from pathlib import Path

ALLOWLIST = set()

def test_no_chained_assignment():
    """
    Ensures that top-level modules and plugins do not use chained assignments
    with mutable values (like `a = b = []` or `a = b = {}`), which can lead to aliasing bugs.
    Enforced by checking `ast.Assign` nodes for multiple targets and mutable values.
    """
    offenders = []

    # Check top-level python files and plugins
    patterns = ('*.py', 'plugins/*.py')
    files_to_check = []
    for pattern in patterns:
        files_to_check.extend(glob.glob(pattern))

    for filename in files_to_check:
        filepath = Path(filename)
        # Skip this file itself if checking top-level, though it's in tests/
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        try:
            tree = ast.parse(content)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and len(node.targets) > 1:
                if isinstance(node.value, (ast.List, ast.Dict, ast.Set)):
                    offenders.append(filename)
                    break  # Record file at most once

    new_offenders = [f for f in offenders if f not in ALLOWLIST]

    assert not new_offenders, (
        "Chained assignments with mutable types (e.g. `a = b = []`) are forbidden to prevent aliasing issues. "
        f"Found offenders in: {new_offenders}"
    )
