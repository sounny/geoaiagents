import ast
import glob
from pathlib import Path

def check_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read(), filename=filepath)

    offenders = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "super":
            if len(node.args) > 0:
                offenders += 1
    return offenders

def test_no_new_explicit_super_calls():
    # Resolve paths relative to the project root
    project_root = Path(__file__).parent.parent
    files = list(project_root.glob("*.py")) + list((project_root / "plugins").glob("*.py"))

    # Allowlist is intentionally empty because there are currently 0 offenders
    # in the top-level .py files and plugins/*.py.
    # Format: 'filename.py': number_of_offenses
    allowlist = {}

    total_offenses = 0
    total_allowed = sum(allowlist.values())

    file_offenses = {}

    for f in files:
        res = check_file(str(f))
        rel_path = f.relative_to(project_root).as_posix()

        # Enforce on a per-file basis
        allowed_count = allowlist.get(rel_path, 0)
        assert res <= allowed_count, (
            f"File {rel_path} has {res} explicit super(Class, self) calls, "
            f"which exceeds its allowed baseline of {allowed_count}."
        )

        if res > 0:
            total_offenses += res
            file_offenses[rel_path] = res

    assert total_offenses <= total_allowed, (
        f"Found {total_offenses} total explicit super(Class, self) calls, "
        f"which exceeds the global baseline of {total_allowed}. "
        f"Current offenses: {file_offenses}"
    )
