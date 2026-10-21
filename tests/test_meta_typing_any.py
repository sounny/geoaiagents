import ast
import glob

ALLOWLIST = {
    "tool_registry.py": 6
}

def count_typing_any_in_file(filepath: str) -> int:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content, filename=filepath)
    except Exception:
        return 0

    count = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.returns:
            for child in ast.walk(node.returns):
                if isinstance(child, ast.Name) and child.id == 'Any':
                    count += 1
                elif isinstance(child, ast.Attribute) and isinstance(child.value, ast.Name) and child.value.id == 'typing' and child.attr == 'Any':
                    count += 1
        elif isinstance(node, ast.arg) and node.annotation:
            for child in ast.walk(node.annotation):
                if isinstance(child, ast.Name) and child.id == 'Any':
                    count += 1
                elif isinstance(child, ast.Attribute) and isinstance(child.value, ast.Name) and child.value.id == 'typing' and child.attr == 'Any':
                    count += 1
        elif isinstance(node, ast.AnnAssign) and node.annotation:
            for child in ast.walk(node.annotation):
                if isinstance(child, ast.Name) and child.id == 'Any':
                    count += 1
                elif isinstance(child, ast.Attribute) and isinstance(child.value, ast.Name) and child.value.id == 'typing' and child.attr == 'Any':
                    count += 1
    return count

def test_no_new_typing_any():
    files_to_check = glob.glob("*.py") + glob.glob("plugins/*.py")

    total_found = 0
    total_allowed = sum(ALLOWLIST.values())

    for filepath in files_to_check:
        total_found += count_typing_any_in_file(filepath)

    assert total_found <= total_allowed, (
        f"Expected at most {total_allowed} uses of typing.Any in annotations, "
        f"but found {total_found}. Please use more specific types."
    )
