import ast
from pathlib import Path
import pytest

# Expected offenders mapping: "filename:ClassName": count
# Example: "webchat.py:WebchatTool": 26
ALLOWLIST = {
    "tool_registry.py:ToolRegistry": 5,
    "webchat.py:GradioLogHandler": 1,
}

def get_python_files():
    root_dir = Path(__file__).parent.parent

    top_level_files = list(root_dir.glob("*.py"))
    plugin_files = list(root_dir.glob("plugins/*.py"))

    return top_level_files + plugin_files

def test_class_method_count():
    root_dir = Path(__file__).parent.parent
    files_to_check = get_python_files()

    errors = []

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
            if isinstance(node, ast.ClassDef):
                method_count = sum(
                    1 for child in node.body
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                )

                if method_count > 25:
                    key = f"{rel_path}:{node.name}"
                    allowed_count = ALLOWLIST.get(key, 0)

                    if method_count > allowed_count:
                        if allowed_count == 0:
                            errors.append(f"{key} has {method_count} methods, which exceeds the limit of 25.")
                        else:
                            errors.append(f"{key} has {method_count} methods, which exceeds its allowlisted baseline of {allowed_count}.")

    if errors:
        pytest.fail("Classes with too many methods found:\n" + "\n".join(errors))
