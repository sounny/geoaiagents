import ast
from pathlib import Path
import pytest

ALLOWLIST = [
]

def get_python_files():
    root_dir = Path(__file__).parent.parent
    top_level_files = list(root_dir.glob("*.py"))
    plugin_files = list(root_dir.glob("plugins/*.py"))
    return top_level_files + plugin_files

def is_ascii(s):
    try:
        s.encode('ascii')
        return True
    except UnicodeEncodeError:
        return False

def test_non_ascii_names():
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
            # Check function, class, or variable names that contain non-ASCII characters
            # Functions and classes have 'name'
            # Variables often have 'id' (in Name nodes), 'arg' (in arg nodes), 'asname' (in alias nodes)
            # Sometimes 'attr' in Attribute nodes
            for attr in ['name', 'id', 'arg', 'asname', 'attr']:
                val = getattr(node, attr, None)
                if isinstance(val, str) and not is_ascii(val):
                    key = f"{rel_path}:{val}"
                    if key not in ALLOWLIST:
                        errors.append(f"{key} contains non-ASCII characters.")

    if errors:
        pytest.fail("Files with non-ASCII names found:\n" + "\n".join(errors))
