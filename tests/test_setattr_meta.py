import ast
from pathlib import Path
import os

def test_no_setattr_builtin_type():
    # Builtin types to check for
    builtin_types = {'list', 'dict', 'str', 'object'}

    offenders = []
    allowlist = {}  # Empty allowlist as we found no current offenders

    project_root = Path(__file__).parent.parent

    # Gather files
    files_to_check = list(project_root.glob('*.py')) + list(project_root.glob('plugins/*.py'))

    for file_path in files_to_check:
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read(), filename=str(file_path))
            except Exception:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id == 'setattr':
                        if len(node.args) >= 1:
                            arg0 = node.args[0]
                            if isinstance(arg0, ast.Name) and arg0.id in builtin_types:
                                # Check allowlist
                                rel_path = file_path.relative_to(project_root).as_posix()
                                if rel_path in allowlist and node.lineno in allowlist[rel_path]:
                                    continue
                                offenders.append(f"{rel_path}:{node.lineno}")

    assert not offenders, f"Found setattr() calls with builtin type as first argument:\n" + "\n".join(offenders)
