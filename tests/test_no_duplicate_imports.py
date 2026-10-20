import ast
import glob
import pytest
from pathlib import Path

# Allowlist for existing offenders: map file path to a list of duplicate names
ALLOWLIST = {
}

def get_top_level_duplicate_imports(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return set()

    imported_names = set()
    duplicates = set()

    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name
                if name in imported_names:
                    duplicates.add(name)
                else:
                    imported_names.add(name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                name = alias.asname or alias.name
                if name in imported_names:
                    duplicates.add(name)
                else:
                    imported_names.add(name)

    return duplicates

def test_no_duplicate_imports():
    files_to_check = glob.glob("*.py") + glob.glob("plugins/*.py")

    errors = []
    for filepath in files_to_check:
        duplicates = get_top_level_duplicate_imports(filepath)
        allowed = ALLOWLIST.get(filepath, [])
        unallowed_duplicates = duplicates - set(allowed)

        if unallowed_duplicates:
            errors.append(f"{filepath} imports the same name twice at top level: {', '.join(unallowed_duplicates)}")

    assert not errors, "\n".join(errors)
