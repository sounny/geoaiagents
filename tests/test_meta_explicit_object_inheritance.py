import ast
import glob
import pytest
from pathlib import Path

# Mapping of file paths to the count of explicit object inheritances.
ALLOWLIST = {
}

def check_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=filepath)
    except Exception:
        return 0

    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                if isinstance(base, ast.Name) and base.id == "object":
                    count += 1
    return count

def test_no_explicit_object_inheritance():
    files = glob.glob("*.py") + glob.glob("plugins/*.py")
    all_offenders = {}

    for f in files:
        count = check_file(f)
        allowed = ALLOWLIST.get(f, 0)

        if count > allowed:
            all_offenders[f] = {"found": count, "allowed": allowed}

    if all_offenders:
        error_messages = [
            f"{f}: found {data['found']}, allowed {data['allowed']}"
            for f, data in all_offenders.items()
        ]
        pytest.fail(
            "Found classes explicitly inheriting from object beyond allowlisted counts:\n" +
            "\n".join(error_messages)
        )
