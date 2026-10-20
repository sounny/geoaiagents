import ast
from pathlib import Path
import pytest

# Expected offenders mapping: "filename:function_name": count
ALLOWLIST = {}

def get_python_files():
    root_dir = Path(__file__).parent.parent

    top_level_files = list(root_dir.glob("*.py"))
    plugin_files = list(root_dir.glob("plugins/*.py"))

    return top_level_files + plugin_files

def test_if_elif_branches_count():
    root_dir = Path(__file__).parent.parent
    files_to_check = get_python_files()

    errors = []
    current_count = 0
    allowlist_total = len(ALLOWLIST)

    for filepath in files_to_check:
        try:
            with filepath.open("r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            errors.append(f"Could not read {filepath}: {e}")
            continue

        try:
            tree = ast.parse(content, filename=str(filepath))
        except SyntaxError as e:
            errors.append(f"Syntax error in {filepath}: {e}")
            continue

        rel_path = filepath.relative_to(root_dir).as_posix()

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if_count = sum(1 for child in ast.walk(node) if isinstance(child, ast.If))

                if if_count > 15:
                    current_count += 1
                    key = f"{rel_path}:{node.name}"
                    allowed_count = ALLOWLIST.get(key, 0)

                    if if_count > allowed_count:
                        if allowed_count == 0:
                            errors.append(f"{key} has {if_count} if/elif branches, which exceeds the limit of 15.")
                        else:
                            errors.append(f"{key} has {if_count} if/elif branches, which exceeds its allowlisted baseline of {allowed_count}.")

    if current_count > allowlist_total:
        errors.append(
            f"Total number of functions with >15 if/elif branches ({current_count}) "
            f"exceeds the allowlisted baseline ({allowlist_total})."
        )

    if errors:
        pytest.fail("Functions with too many if/elif branches found:\n" + "\n".join(errors))
