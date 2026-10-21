import ast
from pathlib import Path

def test_no_except_pass():
    """
    Parses every top-level .py module and plugins/*.py with ast and fails
    if the total count of except handlers whose only body is pass grows
    beyond the current count, with an allowlist for current offenders.
    """
    base_dir = Path(__file__).parent.parent

    # Collect all top-level .py modules and plugins/*.py
    py_files = list(base_dir.glob("*.py")) + list((base_dir / "plugins").glob("*.py"))

    allowlist = {
        'webchat.py'
    }

    total_count = 0

    for file_path in py_files:
        try:
            tree = ast.parse(file_path.read_text(encoding='utf-8'), filename=str(file_path))
        except SyntaxError:
            continue

        file_count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    file_count += 1

        if file_count > 0:
            assert file_path.name in allowlist, f"File {file_path.name} is not in the allowlist but contains an except handler whose only body is pass."

        total_count += file_count

    assert total_count <= 1, f"Total except handler whose only body is pass count grew to {total_count}, expected <= 1"
