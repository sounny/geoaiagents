import ast
from pathlib import Path
import pytest

# Allowlist for existing files that use pickle.load or pickle.loads
# Example: "example_plugin.py"
ALLOWLIST = set()

def find_python_files():
    root_dir = Path(__file__).parent.parent

    # Top-level .py files
    files = list(root_dir.glob("*.py"))

    # plugins/*.py files
    plugins_dir = root_dir / "plugins"
    if plugins_dir.exists() and plugins_dir.is_dir():
        files.extend(plugins_dir.glob("*.py"))

    return files

def check_pickle_usage(filepath: Path):
    if filepath.name in ALLOWLIST:
        return []

    content = filepath.read_text(encoding="utf-8")
    try:
        tree = ast.parse(content, filename=str(filepath))
    except SyntaxError:
        # Ignore syntax errors (handled by other tools/tests if relevant)
        return []

    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "pickle":
                    if node.func.attr in ("load", "loads"):
                        violations.append(f"{filepath.name}:{node.lineno} - pickle.{node.func.attr}() is forbidden.")

    return violations

def test_no_pickle_load():
    python_files = find_python_files()
    all_violations = []

    for filepath in python_files:
        violations = check_pickle_usage(filepath)
        all_violations.extend(violations)

    if all_violations:
        error_msg = "Forbidden usage of pickle.load/pickle.loads found:\n" + "\n".join(all_violations)
        pytest.fail(error_msg)
