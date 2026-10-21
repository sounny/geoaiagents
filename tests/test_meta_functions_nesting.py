import ast
import glob

def test_no_functions_nested_more_than_two_levels_deep():
    """
    Top-level Python modules and plugins (plugins/*.py) must not contain
    functions nested more than two levels deep inside other functions.
    This is enforced by an AST-based pytest meta-test using a count-based allowlist for existing offenders.
    """
    files = glob.glob('*.py') + glob.glob('plugins/*.py')

    # Filter files to exclude tests
    files = [f for f in files if not f.startswith('test_')]

    allowlist = {}
    current_offenders = {}

    for filepath in files:
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read(), filename=filepath)
            except SyntaxError:
                continue

        class Visitor(ast.NodeVisitor):
            def __init__(self):
                self.depth = 0
                self.offenders_count = 0

            def check(self):
                if self.depth > 2:
                    self.offenders_count += 1

            def visit_FunctionDef(self, node):
                self.check()
                self.depth += 1
                self.generic_visit(node)
                self.depth -= 1

            def visit_AsyncFunctionDef(self, node):
                self.check()
                self.depth += 1
                self.generic_visit(node)
                self.depth -= 1

            def visit_Lambda(self, node):
                self.check()
                self.depth += 1
                self.generic_visit(node)
                self.depth -= 1

        visitor = Visitor()
        visitor.visit(tree)
        if visitor.offenders_count > 0:
            current_offenders[filepath] = visitor.offenders_count

    total_offenders = sum(current_offenders.values())
    total_allowed = sum(allowlist.values())

    assert total_offenders <= total_allowed, (
        f"Found {total_offenders} functions nested more than two levels deep "
        f"(allowed {total_allowed}). Offenders: {current_offenders}"
    )

    for f, count in current_offenders.items():
        allowed_count = allowlist.get(f, 0)
        assert count <= allowed_count, (
            f"{f} has {count} functions nested more than two levels deep, "
            f"but only {allowed_count} are allowed."
        )
