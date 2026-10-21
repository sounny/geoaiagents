import ast
import glob
import os
import pytest

# Allowlist for files that contain input() calls and their counts
ALLOWLIST = {
    "dd2dms.py": 1,
    "distance.py": 1,
    "geoai_cli.py": 1,
    "geocode.py": 1,
    "humboldt.py": 1,
}

BASELINE_TOTAL = sum(ALLOWLIST.values())

def get_python_files():
    top_level = glob.glob("*.py")
    plugins = glob.glob("plugins/*.py")
    return top_level + plugins

def count_input_calls_in_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content, filename=filepath)
    except SyntaxError:
        pytest.fail(f"Could not parse {filepath} due to SyntaxError.")
    except Exception as e:
        pytest.fail(f"Could not parse {filepath}: {e}")

    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "input":
                count += 1
    return count

def test_no_new_input_calls():
    files = get_python_files()
    total_input_calls = 0
    errors = []

    for filepath in files:
        basename = os.path.basename(filepath)
        count = count_input_calls_in_file(filepath)
        total_input_calls += count

        allowed = ALLOWLIST.get(basename, 0)
        if count > allowed:
            errors.append(f"{filepath} has {count} input() calls (allowed: {allowed})")

    if total_input_calls > BASELINE_TOTAL:
        errors.append(f"Total input() calls ({total_input_calls}) exceeds baseline ({BASELINE_TOTAL})")

    if errors:
        pytest.fail("Found new input() calls:\n" + "\n".join(errors))
