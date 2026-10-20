import ast
import glob
import pytest

def test_no_bare_raise_outside_except():
    """
    Ensure that top-level .py modules and plugins/*.py do not contain
    bare 'raise' statements outside of an 'except' handler.
    """
    files = glob.glob("*.py") + glob.glob("plugins/*.py")

    # Allowlist for existing offenders (if any). Currently empty.
    allowlist = []

    class RaiseChecker(ast.NodeVisitor):
        def __init__(self, filepath):
            self.filepath = filepath
            self.in_except = 0
            self.errors = []

        def visit_ExceptHandler(self, node):
            self.in_except += 1
            self.generic_visit(node)
            self.in_except -= 1

        def visit_Raise(self, node):
            # A bare raise has node.exc == None
            if node.exc is None and self.in_except == 0:
                self.errors.append(f"{self.filepath}:{node.lineno}")
            self.generic_visit(node)

    all_errors = []
    for filepath in files:
        if filepath in allowlist:
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=filepath)
            except SyntaxError:
                # If there's a syntax error, we ignore it here as other tests or the runner will catch it
                continue

        checker = RaiseChecker(filepath)
        checker.visit(tree)
        all_errors.extend(checker.errors)

    if all_errors:
        pytest.fail("Bare 'raise' found outside except handler:\n" + "\n".join(all_errors))
