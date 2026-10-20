import ast
import glob
from pathlib import Path

# Allowlist for modules that already have nested try blocks deeper than 2.
# Format: { "filename.py": count }
ALLOWLIST = {
}

class TryDepthVisitor(ast.NodeVisitor):
    def __init__(self):
        self.try_depth = 0
        self.violations = 0

    def visit_Try(self, node):
        self.try_depth += 1
        if self.try_depth > 2:
            self.violations += 1
        self.generic_visit(node)
        self.try_depth -= 1

    def visit_TryStar(self, node):
        self.try_depth += 1
        if self.try_depth > 2:
            self.violations += 1
        self.generic_visit(node)
        self.try_depth -= 1


def test_no_deep_nested_try_blocks():
    """
    Ensure top-level Python modules and plugins/*.py do not increase
    their count of try blocks nested more than two levels deep beyond
    the current baseline.
    """
    repo_root = Path(__file__).parent.parent
    files = set(repo_root.glob("*.py")) | set(repo_root.glob("plugins/*.py"))

    total_violations = 0
    total_allowed = sum(ALLOWLIST.values())

    for filename in files:
        filepath = Path(filename)
        if not filepath.is_file():
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()

        try:
            tree = ast.parse(source, filename=filename)
        except SyntaxError:
            continue

        visitor = TryDepthVisitor()
        visitor.visit(tree)

        total_violations += visitor.violations

    assert total_violations <= total_allowed, (
        f"Found {total_violations} try blocks nested more than 2 levels deep, "
        f"which exceeds the allowed baseline of {total_allowed}. "
        f"Please refactor deeply nested try blocks."
    )
