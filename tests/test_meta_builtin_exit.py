import ast
import glob
import os
import pytest

def test_no_builtin_exit_or_quit():
    """
    Ensure no top-level .py module or plugins/*.py calls exit() or quit() builtins.
    Prefer sys.exit() instead.
    """
    # Allowlist for current offenders
    allowlist = set()

    files_to_check = glob.glob("*.py") + glob.glob("plugins/*.py")

    class ExitVisitor(ast.NodeVisitor):
        def __init__(self):
            self.bad_calls = []

        def visit_Call(self, node):
            if isinstance(node.func, ast.Name):
                if node.func.id in ("exit", "quit"):
                    self.bad_calls.append((node.func.id, node.lineno))
            self.generic_visit(node)

    offenders = []

    for filepath in files_to_check:
        if filepath in allowlist:
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=filepath)
            except SyntaxError:
                continue

        visitor = ExitVisitor()
        visitor.visit(tree)

        if visitor.bad_calls:
            calls_str = ", ".join(f"{name}() at line {line}" for name, line in visitor.bad_calls)
            offenders.append(f"{filepath}: {calls_str}")

    if offenders:
        pytest.fail(
            "Found calls to exit() or quit() builtins. Prefer sys.exit():\n" +
            "\n".join(offenders)
        )
