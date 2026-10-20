import ast
from pathlib import Path

def test_no_new_range_len_loops():
    files_to_check = list(Path('.').glob('*.py')) + list(Path('plugins').glob('*.py'))

    # Allowlist of files and the line numbers where range(len(...)) is currently used
    allowlist = {}

    current_count = 0
    errors = []

    for file_path in files_to_check:
        if not file_path.is_file():
            continue

        source = file_path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                iter_node = node.iter
                if isinstance(iter_node, ast.Call) and isinstance(iter_node.func, ast.Name) and iter_node.func.id == 'range':
                    if len(iter_node.args) == 1:
                        arg = iter_node.args[0]
                        if isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name) and arg.func.id == 'len':
                            current_count += 1
                            # Check against allowlist
                            allowed_lines = allowlist.get(str(file_path), [])
                            if node.lineno not in allowed_lines:
                                errors.append(f"{file_path}:{node.lineno}")

    allowed_count = sum(len(lines) for lines in allowlist.values())

    assert not errors, (
        f"Found new 'for i in range(len(x))' loops. "
        f"Total count {current_count} exceeds allowed {allowed_count}. "
        f"New offenders: {errors}"
    )
    assert current_count <= allowed_count, "Total count of range(len(x)) loops has grown."
