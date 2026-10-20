import ast
import glob
import os
import pytest

ALLOWLIST = [
    # Format: (filename, variable_name)
    # Example: ("humboldt.py", "x")
]

def test_no_self_assignment():
    files_to_check = glob.glob("*.py") + glob.glob("plugins/*.py")

    new_offenders = []

    for filepath in files_to_check:
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=filepath)
            except SyntaxError:
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                if isinstance(node.value, ast.Name):
                    val_id = node.value.id
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == val_id:
                            # It's a self assignment like `x = x`
                            offender = (filepath, target.id)
                            if offender not in ALLOWLIST:
                                new_offenders.append(f"{filepath}:{node.lineno} -> {target.id} = {target.id}")

    assert not new_offenders, "Found new self-assignments (x = x):\n" + "\n".join(new_offenders)
