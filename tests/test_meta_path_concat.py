import ast
import glob

ALLOWLIST = {}

def count_top_level_adds_with_slash(tree):
    class Visitor(ast.NodeVisitor):
        def __init__(self):
            self.adds_with_slashes = set()
            self.parent_map = {}

        def is_slash_literal(self, n):
            return isinstance(n, ast.Constant) and isinstance(n.value, str) and "/" in n.value

        def get_all_operands(self, n):
            operands = []
            if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
                operands.extend(self.get_all_operands(n.left))
                operands.extend(self.get_all_operands(n.right))
            else:
                operands.append(n)
            return operands

        def visit(self, n):
            for child in ast.iter_child_nodes(n):
                self.parent_map[child] = n
            super().visit(n)

        def visit_BinOp(self, n):
            self.generic_visit(n)
            if isinstance(n.op, ast.Add):
                parent = self.parent_map.get(n)
                if isinstance(parent, ast.BinOp) and isinstance(parent.op, ast.Add):
                    return  # not top-level
                operands = self.get_all_operands(n)
                if any(self.is_slash_literal(op) for op in operands):
                    self.adds_with_slashes.add(n)

    v = Visitor()
    v.visit(tree)
    return len(v.adds_with_slashes)

def test_no_new_path_concatenations():
    files = glob.glob("*.py") + glob.glob("plugins/*.py")

    total_offenders = 0
    total_allowed = sum(ALLOWLIST.values())

    for f in files:
        if f.startswith("test_") or f.startswith("conftest"):
            continue
        try:
            with open(f, "r", encoding="utf-8") as file:
                content = file.read()
            tree = ast.parse(content, filename=f)
            count = count_top_level_adds_with_slash(tree)
            total_offenders += count
        except SyntaxError:
            continue

    assert total_offenders <= total_allowed, (
        f"Expected at most {total_allowed} string + concatenations whose operands include a '/' literal (path building), "
        f"found {total_offenders}. Use os.path.join or pathlib instead."
    )
