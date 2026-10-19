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

    for filepath in files:
        if filepath.startswith('tests/'):
            continue

        with open(filepath, 'r', encoding='utf-8') as file:
            tree = ast.parse(file.read(), filename=filepath)

        visitor = OpenVisitor(filepath)
        visitor.visit(tree)

        for line in visitor.violations:
            violation = f"{filepath}:{line}"
            if violation not in ALLOWLIST:
                offenders.append(violation)

    assert not offenders, f"open() called outside with statement in: {offenders}"
