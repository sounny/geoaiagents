import ast
import glob

class TryDepthVisitor(ast.NodeVisitor):
    def __init__(self):
        self.depth = 0
        self.deep_count = 0

    def visit_Try(self, node):
        self.depth += 1
        if self.depth > 2:
            self.deep_count += 1
        self.generic_visit(node)
        self.depth -= 1

def test_no_increase_nested_try_blocks():
    files = glob.glob("*.py") + glob.glob("plugins/*.py")

    # We found 0 offenders currently.
    allowlist = {}

    total_deep_try = 0
    for f in files:
        with open(f, "r", encoding="utf-8") as file:
            content = file.read()

        try:
            tree = ast.parse(content)
        except SyntaxError:
            continue

        visitor = TryDepthVisitor()
        visitor.visit(tree)

        count = visitor.deep_count

        if count > 0:
            allowed = allowlist.get(f, 0)
            assert count <= allowed, f"File {f} has {count} deeply nested try blocks, which is more than allowed {allowed}."
            total_deep_try += count

    assert total_deep_try <= sum(allowlist.values()), "Total deeply nested try blocks increased beyond baseline."
