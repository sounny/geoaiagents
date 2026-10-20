import ast
import glob

def test_no_deep_nesting():
    """
    Parses every top-level .py module and plugins/*.py with ast and fails when
    a function definition nests more than three levels of def/lambda deep.
    """
    files = glob.glob('*.py') + glob.glob('plugins/*.py')

    allowlist = {}
    offenders = {}

    class NestingVisitor(ast.NodeVisitor):
        def __init__(self):
            self.depth = 0
            self.violations = []

        def visit_FunctionDef(self, node):
            self.depth += 1
            if self.depth > 3:
                self.violations.append(node.name)
            self.generic_visit(node)
            self.depth -= 1

        def visit_AsyncFunctionDef(self, node):
            self.depth += 1
            if self.depth > 3:
                self.violations.append(node.name)
            self.generic_visit(node)
            self.depth -= 1

        def visit_Lambda(self, node):
            self.depth += 1
            if self.depth > 3:
                self.violations.append("<lambda>")
            self.generic_visit(node)
            self.depth -= 1

    for filepath in files:
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read(), filename=filepath)
            except SyntaxError:
                continue

        visitor = NestingVisitor()
        visitor.visit(tree)

        if visitor.violations:
            allowed = allowlist.get(filepath, [])
            filtered_violations = [v for v in visitor.violations if v not in allowed]
            if filtered_violations:
                offenders[filepath] = filtered_violations

    assert not offenders, f"Functions must not nest more than 3 levels deep: {offenders}"
