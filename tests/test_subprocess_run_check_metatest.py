import ast
from pathlib import Path

# Provide baseline allowlist using relative paths
ALLOWLIST = []
BASELINE_COUNT = 0

def test_subprocess_run_check_argument():
    base_dir = Path(__file__).parent.parent
    target_files = list(base_dir.glob('*.py')) + list((base_dir / 'plugins').glob('*.py'))

    offenders = []

    class SubprocessRunChecker(ast.NodeVisitor):
        def __init__(self, filepath):
            self.filepath = filepath

        def visit_Call(self, node):
            self.generic_visit(node)
            is_subprocess_run = False

            # Check if it's a subprocess.run call
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == 'run':
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == 'subprocess':
                        is_subprocess_run = True

            if is_subprocess_run:
                # Check for the 'check' keyword argument
                has_check = any(keyword.arg == 'check' for keyword in node.keywords)

                if not has_check:
                    rel_path = str(Path(self.filepath).relative_to(base_dir))
                    offenders.append(f"{rel_path}:{node.lineno}")

    for p in target_files:
        try:
            with open(p, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content, filename=str(p))
            checker = SubprocessRunChecker(str(p))
            checker.visit(tree)
        except Exception:
            pass

    unallowed_offenders = [o for o in offenders if o not in ALLOWLIST]

    assert len(unallowed_offenders) <= BASELINE_COUNT, (
        f"Found {len(unallowed_offenders)} subprocess.run calls without 'check=' "
        f"(baseline is {BASELINE_COUNT}). Offenders: {unallowed_offenders}"
    )
