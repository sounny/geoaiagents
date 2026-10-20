import ast
from pathlib import Path
import pytest

# Allowlist mapping filename relative to project root to expected counts of pickle.load/loads calls
# Example: {"plugins/example_plugin.py": 2}
ALLOWLIST = {}

def get_python_files():
    root_dir = Path(__file__).parent.parent

    # Top-level .py files
    files = list(root_dir.glob("*.py"))

    # plugins/*.py files
    plugins_dir = root_dir / "plugins"
    if plugins_dir.exists() and plugins_dir.is_dir():
        files.extend(plugins_dir.glob("*.py"))

    return root_dir, files

def test_no_pickle_load():
    """
    Parses every top-level .py module and plugins/*.py with ast and fails if the total
    count of pickle.load and pickle.loads calls grows beyond the current count,
    with an allowlist for current offenders.
    """
    root_dir, files = get_python_files()

    current_offenders = {}

    for filepath in files:
        if not filepath.is_file():
            continue

        content = filepath.read_text(encoding="utf-8")
        try:
            tree = ast.parse(content, filename=str(filepath))
        except SyntaxError:
            continue

        count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "pickle":
                        if node.func.attr in ("load", "loads"):
                            count += 1

        if count > 0:
            # Use relative path as string to avoid name collisions
            rel_path = str(filepath.relative_to(root_dir)).replace('\\', '/')
            current_offenders[rel_path] = count

    total_offenders = sum(current_offenders.values())
    total_allowed = sum(ALLOWLIST.values())

    error_msg = f"Found {total_offenders} pickle.load/loads calls (allowed {total_allowed}). Offenders: {current_offenders}"
    assert total_offenders <= total_allowed, error_msg

    for f, count in current_offenders.items():
        allowed_count = ALLOWLIST.get(f, 0)
        assert count <= allowed_count, f"{f} has {count} pickle.load/loads calls, but only {allowed_count} are allowed."
