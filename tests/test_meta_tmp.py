import ast
import os
from pathlib import Path

# Allowlist for existing files that use /tmp/
ALLOWLIST = []

def test_no_tmp_string_literals():
    base_dir = Path(__file__).parent.parent
    offenders = []

    def check_file(filepath: Path):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    if node.value.startswith('/tmp/'):
                        rel_path = filepath.relative_to(base_dir).as_posix()
                        if rel_path not in ALLOWLIST:
                            offenders.append(f"{rel_path}:{node.lineno}: found '{node.value}'")
        except SyntaxError:
            pass

    # Check top-level python files
    for filepath in base_dir.glob('*.py'):
        if filepath.is_file():
            check_file(filepath)

    # Check python files in plugins
    plugins_dir = base_dir / 'plugins'
    if plugins_dir.is_dir():
        for filepath in plugins_dir.glob('*.py'):
            if filepath.is_file():
                check_file(filepath)

    assert not offenders, (
        "String literals starting with /tmp/ found (use tempfile instead):\n" + "\n".join(offenders)
    )
