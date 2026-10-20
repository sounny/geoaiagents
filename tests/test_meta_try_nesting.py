import ast
import glob
import pytest

def test_nested_try_blocks():
    """
    Parses every top-level .py module and plugins/*.py with ast and fails if there are try statements
    nested more than two levels deep and if the total grows beyond the current count, with an allowlist for current offenders.
    """
    files = glob.glob('*.py') + glob.glob('plugins/*.py')

    allowlist = {} # Current offenders allowlist
    current_offenders = {}

    class TryVisitor(ast.NodeVisitor):
        def __init__(self, filename):
            self.filename = filename
            self.try_depth = 0
            self.offending_tries = []

        def visit_Try(self, node):
            self.try_depth += 1
            if self.try_depth > 2:
                self.offending_tries.append(node.lineno)
            self.generic_visit(node)
            self.try_depth -= 1

        def visit_TryStar(self, node):
            self.try_depth += 1
            if self.try_depth > 2:
                self.offending_tries.append(node.lineno)
            self.generic_visit(node)
            self.try_depth -= 1

    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        try:
            tree = ast.parse(content)
        except SyntaxError:
            continue
        visitor = TryVisitor(f)
        visitor.visit(tree)
        if visitor.offending_tries:
            current_offenders[f] = len(visitor.offending_tries)

    total_offenders = sum(current_offenders.values())
    total_allowed = sum(allowlist.values())

    error_msg = f"Found {total_offenders} try statements nested more than two levels deep (allowed {total_allowed}). Offenders: {current_offenders}"
    assert total_offenders <= total_allowed, error_msg

    for f, count in current_offenders.items():
        allowed_count = allowlist.get(f, 0)
        assert count <= allowed_count, f"{f} has {count} try statements nested more than two levels deep, but only {allowed_count} are allowed."
