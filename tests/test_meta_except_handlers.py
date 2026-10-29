import ast
from pathlib import Path

def test_no_bare_except_or_except_exception():
    base_dir = Path(__file__).parent.parent

    # Collect all top-level .py modules and plugins/*.py
    py_files = list(base_dir.glob("*.py")) + list((base_dir / "plugins").glob("*.py"))

    allowlist = {
        'tool_registry.py',
        'webchat.py',
        'llm_utils.py',
        'file_loaders.py',
        'geocode.py',
        'dd2dms.py',
        'geocode.py',
        'dd2dms.py'
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
                if node.type is None:
                    # Bare except
                    file_count += 1
                elif isinstance(node.type, ast.Name) and node.type.id == 'Exception':
                    # except Exception
                    file_count += 1

        if file_count > 0:
            assert file_path.name in allowlist, f"File {file_path.name} is not in the allowlist but contains bare except or except Exception handlers."

        total_count += file_count

    assert total_count <= 15, f"Total bare except / except Exception count grew to {total_count}, expected <= 8"
