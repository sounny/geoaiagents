import ast
from pathlib import Path

# Expected offenders mapping: "filename.py": count
# Note: we are strictly following "fails if the total grows beyond the current count, with an allowlist for current offenders"
ALLOWLIST = {
    "webchat.py": 2,
}

def get_python_files():
    """Get all top-level .py files and .py files in plugins/ directory."""
    root_dir = Path(__file__).parent.parent
    top_level_files = list(root_dir.glob("*.py"))
    plugin_files = list(root_dir.glob("plugins/*.py"))
    return top_level_files + plugin_files

def check_module_level_lowercase_literal_assignment(filepath):
    """Check a file for module-level assignments of list, dict, or set literals to lowercase names."""
    try:
        with filepath.open("r", encoding="utf-8") as f:
            source = f.read()
    except Exception:
        return 0

    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError:
        return 0

    count = 0

    # We only check the module body (top-level statements)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if isinstance(node.value, (ast.List, ast.Dict, ast.Set)):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.islower():
                        count += 1

        elif isinstance(node, ast.AnnAssign):
            if node.value is not None and isinstance(node.value, (ast.List, ast.Dict, ast.Set)):
                if isinstance(node.target, ast.Name) and node.target.id.islower():
                    count += 1

    return count

def test_no_module_level_lowercase_literal_assignment():
    """Meta-test to ensure module-level assignments of list, dict, or set literals to lowercase names do not increase."""
    root_dir = Path(__file__).parent.parent
    files = get_python_files()

    errors = []

    for filepath in files:
        rel_path = filepath.relative_to(root_dir).as_posix()
        count = check_module_level_lowercase_literal_assignment(filepath)

        allowed_count = ALLOWLIST.get(rel_path, 0)

        if count > allowed_count:
            if allowed_count == 0:
                errors.append(f"'{rel_path}' has {count} module-level assignment(s) of list/dict/set literals to lowercase names.")
            else:
                errors.append(f"'{rel_path}' has {count} module-level assignment(s) of list/dict/set literals to lowercase names, which exceeds its allowlisted baseline of {allowed_count}.")

    if errors:
        import pytest
        pytest.fail("Module-level lowercase literal assignment count increased:\n" + "\n".join(errors))
