import ast
import glob
import itertools
from pathlib import Path

# Allowlist for existing offenders.
# Format: {"filename": [line_numbers]}
ALLOWLIST = {
    # Currently empty, as no offenders were found
}

def test_meta_requests_timeout():
    """
    Ensure all requests.get, post, put, delete, request calls pass a timeout= argument.
    """
    offenders = []

    # Get all top-level .py files and plugins/*.py files
    files_to_check = itertools.chain(
        glob.glob('*.py'),
        glob.glob('plugins/*.py')
    )

    for filename in files_to_check:
        filepath = Path(filename)
        if not filepath.is_file():
            continue

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=filename)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check if it's a call to requests.xxx
                if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                    if node.func.value.id == 'requests' and node.func.attr in ('get', 'post', 'put', 'delete', 'request'):
                        has_timeout = False
                        for kw in node.keywords:
                            if kw.arg == 'timeout':
                                has_timeout = True
                                break

                        if not has_timeout:
                            # Check allowlist
                            allowed_lines = ALLOWLIST.get(filename, [])
                            if node.lineno not in allowed_lines:
                                offenders.append(f"{filename}:{node.lineno}")

    assert not offenders, "Found requests calls without timeout= argument: " + ", ".join(offenders)
