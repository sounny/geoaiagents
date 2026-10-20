import ast
import glob
from pathlib import Path

ALLOWLIST = set()

def test_no_relative_imports_beyond_toplevel():
    """
    Ensures that top-level modules and plugins do not contain relative imports
    that go beyond the top-level package (too many leading dots).
    """
    files_to_check = glob.glob("*.py") + glob.glob("plugins/*.py")
    violations = []

    for filepath in files_to_check:
        if filepath in ALLOWLIST:
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=filepath)
            except SyntaxError:
                continue

        path_obj = Path(filepath)
        max_allowed_level = len(path_obj.parents)

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.level is not None and node.level > max_allowed_level:
                    violations.append(
                        f"{filepath}:{node.lineno} (level {node.level} goes beyond top-level package)"
                    )

    assert not violations, "Found relative imports going beyond the top-level package:\n" + "\n".join(violations)
