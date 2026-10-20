import ast
import glob


def test_meta_comprehensions():
    """
    Parses every top-level .py module and plugins/*.py with ast and fails
    counts comprehensions with more than two for clauses and fails if the
    total grows beyond the current count, with an allowlist for current
    offenders.
    """
    files = glob.glob("*.py") + glob.glob("plugins/*.py")

    allowlist = {}  # Current offenders allowlist
    current_offenders = {}

    class ComprehensionVisitor(ast.NodeVisitor):
        def __init__(self):
            self.count = 0

        def check_generators(self, generators):
            if len(generators) > 2:
                self.count += 1

        def visit_ListComp(self, node):
            self.check_generators(node.generators)
            self.generic_visit(node)

        def visit_SetComp(self, node):
            self.check_generators(node.generators)
            self.generic_visit(node)

        def visit_DictComp(self, node):
            self.check_generators(node.generators)
            self.generic_visit(node)

        def visit_GeneratorExp(self, node):
            self.check_generators(node.generators)
            self.generic_visit(node)

    for f in files:
        with open(f, "r", encoding="utf-8") as file:
            content = file.read()
        try:
            tree = ast.parse(content)
        except SyntaxError:
            continue
        visitor = ComprehensionVisitor()
        visitor.visit(tree)
        if visitor.count > 0:
            current_offenders[f] = visitor.count

    total_offenders = sum(current_offenders.values())
    total_allowed = sum(allowlist.values())

    error_msg = (
        f"Found {total_offenders} comprehensions with more than two "
        f"for clauses (allowed {total_allowed}). "
        f"Offenders: {current_offenders}"
    )
    assert total_offenders <= total_allowed, error_msg

    for f, count in current_offenders.items():
        allowed_count = allowlist.get(f, 0)
        assert count <= allowed_count, (
            f"{f} has {count} comprehensions with >2 for clauses, "
            f"but only {allowed_count} are allowed."
        )
