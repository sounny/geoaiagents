import ast
import glob
import os

ALLOWLIST = {
    'tool_registry.py': 1,
    'geoai_cli.py': 1,
    'humboldt.py': 1,
}

def test_no_new_three_arg_getattr():
    files = glob.glob('*.py') + glob.glob('plugins/*.py')
    total_offenses = 0
    current_offenses = {}

    for filepath in files:
        with open(filepath, 'r') as f:
            try:
                tree = ast.parse(f.read(), filename=filepath)
            except Exception as e:
                # Assuming valid syntax for py files
                continue

        count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'getattr':
                    if len(node.args) == 3:
                        count += 1

        if count > 0:
            current_offenses[filepath] = count
            total_offenses += count

    allowed_total = sum(ALLOWLIST.values())

    assert total_offenses <= allowed_total, f"Found new 3-argument getattr calls! Current total: {total_offenses}, Allowed: {allowed_total}. Breakdown: {current_offenses}"
