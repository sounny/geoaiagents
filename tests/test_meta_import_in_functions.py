import ast
import glob
import pytest

def test_no_imports_in_functions():
    """
    Parses every top-level .py module and plugins/*.py with ast and counts import
    statements inside function bodies. Fails if the total grows beyond the current
    count, with an allowlist for current offenders.
    """
    files = glob.glob('*.py') + glob.glob('plugins/*.py')

    allowlist = {
        'geoai_cli.py': 1,
        'geocode.py': 1,
        'humboldt.py': 2,
    }

    current_offenders = {}

    class ImportVisitor(ast.NodeVisitor):
        def __init__(self, filename):
            self.filename = filename
            self.count = 0
            self.in_function = False

        def visit_FunctionDef(self, node):
            old_in_function = self.in_function
            self.in_function = True
            self.generic_visit(node)
            self.in_function = old_in_function

        def visit_AsyncFunctionDef(self, node):
            old_in_function = self.in_function
            self.in_function = True
            self.generic_visit(node)
            self.in_function = old_in_function

        def visit_Import(self, node):
            if self.in_function:
                self.count += 1
            self.generic_visit(node)

        def visit_ImportFrom(self, node):
            if self.in_function:
                self.count += 1
            self.generic_visit(node)

    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        try:
            tree = ast.parse(content)
        except SyntaxError:
            continue
        visitor = ImportVisitor(f)
        visitor.visit(tree)
        if visitor.count > 0:
            current_offenders[f] = visitor.count

    total_offenders = sum(current_offenders.values())
    total_allowed = sum(allowlist.values())

    error_msg = f"Found {total_offenders} imports inside functions (allowed {total_allowed}). Offenders: {current_offenders}"
    assert total_offenders <= total_allowed, error_msg

    for f, count in current_offenders.items():
        allowed_count = allowlist.get(f, 0)
        assert count <= allowed_count, f"{f} has {count} imports inside functions, but only {allowed_count} are allowed."
