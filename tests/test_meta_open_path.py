import ast
from pathlib import Path
import pytest

ALLOWED_OFFENDERS = {}

def get_open_path_count(filepath: str) -> int:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
    except Exception:
        return 0

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return 0

    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "open":
                if node.args:
                    first_arg = node.args[0]
                    if isinstance(first_arg, ast.Call):
                        func = first_arg.func
                        # Match open(Path(...)) or open(pathlib.Path(...))
                        if isinstance(func, ast.Name) and func.id == "Path":
                            count += 1
                        elif isinstance(func, ast.Attribute) and func.attr == "Path":
                            count += 1
    return count

def test_meta_no_open_path_calls():
    repo_root = Path(__file__).parent.parent
    top_level_files = list(repo_root.glob("*.py"))
    plugin_files = list((repo_root / "plugins").glob("*.py"))

    all_files = top_level_files + plugin_files

    offenders = []

    for filepath in all_files:
        rel_path = filepath.relative_to(repo_root).as_posix()
        count = get_open_path_count(str(filepath))
        allowed = ALLOWED_OFFENDERS.get(rel_path, 0)

        if count > allowed:
            offenders.append(f"{rel_path}: found {count}, allowed {allowed}")

    if offenders:
        pytest.fail(
            "Found files with open(Path(...)) exceeding allowed baseline:\n" +
            "\n".join(offenders) +
            "\n\nPrefer Path(...).open() instead."
        )
