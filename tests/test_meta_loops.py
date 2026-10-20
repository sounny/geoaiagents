import ast
import glob
import pytest

def test_unused_loop_vars():
    """
    Parses every top-level .py module and plugins/*.py with ast and fails if there are loops
    whose target variable is never referenced in the loop body (not underscore-prefixed)
    and if the total grows beyond the current count, with an allowlist for current offenders.
    """
    files = glob.glob('*.py') + glob.glob('plugins/*.py')

    allowlist = {} # Current offenders allowlist
    current_offenders = {}

    class LoopVisitor(ast.NodeVisitor):
        def __init__(self, filename):
            self.offending_loops = []
            self.filename = filename

        def visit_For(self, node):
            self.check_loop(node)
            self.generic_visit(node)

        def visit_AsyncFor(self, node):
            self.check_loop(node)
            self.generic_visit(node)

        def check_loop(self, node):
            targets = []
            def get_targets(n):
                if isinstance(n, ast.Name):
                    targets.append(n.id)
                elif isinstance(n, (ast.Tuple, ast.List)):
                    for elt in n.elts:
                        get_targets(elt)
                elif isinstance(n, ast.Starred):
                    get_targets(n.value)

            get_targets(node.target)

            accessed = set()
            class AccessVisitor(ast.NodeVisitor):
                def visit_Name(self, n):
                    if isinstance(n.ctx, (ast.Load, ast.Del)):
                        accessed.add(n.id)
                    self.generic_visit(n)

            visitor = AccessVisitor()
            for stmt in node.body + node.orelse:
                visitor.visit(stmt)

            for t in targets:
                if not t.startswith('_') and t not in accessed:
                    self.offending_loops.append((node.lineno, t))

    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        try:
            tree = ast.parse(content)
        except SyntaxError:
            continue
        visitor = LoopVisitor(f)
        visitor.visit(tree)
        if visitor.offending_loops:
            current_offenders[f] = len(visitor.offending_loops)

    total_offenders = sum(current_offenders.values())
    total_allowed = sum(allowlist.values())

    error_msg = f"Found {total_offenders} unused loop variables (allowed {total_allowed}). Offenders: {current_offenders}"
    assert total_offenders <= total_allowed, error_msg

    for f, count in current_offenders.items():
        allowed_count = allowlist.get(f, 0)
        assert count <= allowed_count, f"{f} has {count} unused loop variables, but only {allowed_count} are allowed."
