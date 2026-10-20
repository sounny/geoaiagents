import ast
import glob

ALLOWLIST = []

def test_open_called_inside_with_statement():
    files = glob.glob('*.py') + glob.glob('plugins/*.py')
    offenders = []

    class OpenVisitor(ast.NodeVisitor):
        def __init__(self, filename):
            self.filename = filename
            self.violations = []
            self.in_with_context = False

        def visit_With(self, node):
            for item in node.items:
                self.in_with_context = True
                self.visit(item.context_expr)
                self.in_with_context = False
            for stmt in node.body:
                self.visit(stmt)

        def visit_AsyncWith(self, node):
            for item in node.items:
                self.in_with_context = True
                self.visit(item.context_expr)
                self.in_with_context = False
            for stmt in node.body:
                self.visit(stmt)

        def visit_Call(self, node):
            if isinstance(node.func, ast.Name) and node.func.id == 'open':
                if not self.in_with_context:
                    self.violations.append(node.lineno)
            self.generic_visit(node)

    total_offenders = 0
    total_allowed = len(ALLOWLIST)

    for filepath in files:
        if filepath.startswith('tests/'):
            continue

        with open(filepath, 'r', encoding='utf-8') as file:
            try:
                tree = ast.parse(file.read(), filename=filepath)
            except SyntaxError:
                continue

        visitor = OpenVisitor(filepath)
        visitor.visit(tree)

        for line in visitor.violations:
            violation = f"{filepath}:{line}"
            offenders.append(violation)
            total_offenders += 1

    assert total_offenders <= total_allowed, (
        f"Expected at most {total_allowed} open() calls outside with statement, "
        f"found {total_offenders}: {offenders}"
    )

    # Make sure offenders found are actually in the allowlist
    new_offenders = [o for o in offenders if o not in ALLOWLIST]
    assert not new_offenders, f"New open() calls outside with statement found: {new_offenders}"

