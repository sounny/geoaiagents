import ast
import glob
import pytest

def test_no_imports_in_loops():
    """
    Ensure no import statements are found inside for or while loop bodies.
    """
    files_to_check = glob.glob("*.py") + glob.glob("plugins/*.py")

    # allowlist for current offenders
    allowlist = []

    offenders = []

    class Visitor(ast.NodeVisitor):
        def __init__(self, filepath):
            self.filepath = filepath
            self.in_loop = 0

        def visit_For(self, node):
            self.in_loop += 1
            self.generic_visit(node)
            self.in_loop -= 1

        def visit_While(self, node):
            self.in_loop += 1
            self.generic_visit(node)
            self.in_loop -= 1

        def visit_AsyncFor(self, node):
            self.in_loop += 1
            self.generic_visit(node)
            self.in_loop -= 1

        def visit_Import(self, node):
            if self.in_loop > 0 and self.filepath not in allowlist:
                offenders.append((self.filepath, node.lineno))
            self.generic_visit(node)

        def visit_ImportFrom(self, node):
            if self.in_loop > 0 and self.filepath not in allowlist:
                offenders.append((self.filepath, node.lineno))
            self.generic_visit(node)

    for filepath in files_to_check:
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=filepath)
                Visitor(filepath).visit(tree)
            except SyntaxError:
                pass

    if offenders:
        msg = "Found import statements inside loops:\n"
        for filepath, lineno in offenders:
            msg += f"  {filepath}:{lineno}\n"
        pytest.fail(msg)
