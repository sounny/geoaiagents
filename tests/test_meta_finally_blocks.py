import ast
from pathlib import Path

ALLOWLIST = set()

def test_no_control_flow_in_finally():
    """
    Test that top-level modules and plugins do not contain return, break, or continue
    statements inside finally blocks.
    """
    project_root = Path(__file__).resolve().parent.parent

    files_to_check = []
    # Top-level python files
    for p in project_root.iterdir():
        if p.is_file() and p.suffix == '.py':
            files_to_check.append(p)

    # Plugins python files
    plugins_dir = project_root / 'plugins'
    if plugins_dir.is_dir():
        for p in plugins_dir.iterdir():
            if p.is_file() and p.suffix == '.py':
                files_to_check.append(p)

    offenders = []

    for file_path in files_to_check:
        if file_path.name in ALLOWLIST:
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)
        except Exception:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Try) and node.finalbody:
                for finally_stmt in node.finalbody:
                    for subnode in ast.walk(finally_stmt):
                        if isinstance(subnode, (ast.Return, ast.Break, ast.Continue)):
                            offenders.append(f"{file_path.name}:{subnode.lineno}")

    assert not offenders, f"Found return/break/continue inside finally block in: {offenders}"
