import ast
import glob
from pathlib import Path

def test_no_functions_nested_more_than_two_levels_deep():
    """
    Top-level Python modules and plugins (plugins/*.py) must not contain
    functions nested more than two levels deep inside other functions.
    This is enforced by an AST-based pytest meta-test using an allowlist for existing offenders.
    """
    files = glob.glob('*.py') + glob.glob('plugins/*.py')

    # Filter files to exclude tests
    files = [f for f in files if not f.startswith('test_')]

    offenders = []

    for filepath in files:
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read(), filename=filepath)
            except SyntaxError:
                continue

        class Visitor(ast.NodeVisitor):
            def __init__(self):
                self.depth = 0

            def check(self, node, name):
                if self.depth > 2:
                    offenders.append(f"{filepath}:{node.lineno} {name}")

            def visit_FunctionDef(self, node):
                self.check(node, node.name)
                self.depth += 1
                self.generic_visit(node)
                self.depth -= 1

            def visit_AsyncFunctionDef(self, node):
                self.check(node, node.name)
                self.depth += 1
                self.generic_visit(node)
                self.depth -= 1

            def visit_Lambda(self, node):
                self.check(node, '<lambda>')
                self.depth += 1
                self.generic_visit(node)
                self.depth -= 1

        Visitor().visit(tree)

    allowlist = []

    unallowed_offenders = [o for o in offenders if o not in allowlist]

    assert not unallowed_offenders, f"Found functions nested more than two levels deep: {unallowed_offenders}"
