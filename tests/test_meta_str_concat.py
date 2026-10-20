import ast
import glob
import os

ALLOWLIST = {}

class StringConcatVisitor(ast.NodeVisitor):
    def __init__(self):
        self.str_names = set()
        self.loop_depth = 0
        self.count = 0

    def visit_Assign(self, node):
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.str_names.add(target.id)
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        if node.value is not None:
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                if isinstance(node.target, ast.Name):
                    self.str_names.add(node.target.id)
        self.generic_visit(node)

    def visit_For(self, node):
        self.loop_depth += 1
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_While(self, node):
        self.loop_depth += 1
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_AsyncFor(self, node):
        self.loop_depth += 1
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_AugAssign(self, node):
        if self.loop_depth > 0:
            if isinstance(node.op, ast.Add):
                if isinstance(node.target, ast.Name):
                    if node.target.id in self.str_names:
                        self.count += 1
        self.generic_visit(node)

def test_no_new_string_concat_in_loops():
    files = glob.glob("*.py") + glob.glob("plugins/*.py")

    total_offenders = 0
    total_allowed = sum(ALLOWLIST.values())

    for f in files:
        if f.startswith("test_") or f.startswith("conftest"):
            continue
        with open(f, "r", encoding="utf-8") as file:
            try:
                tree = ast.parse(file.read(), filename=f)
                v = StringConcatVisitor()
                v.visit(tree)
                total_offenders += v.count
            except Exception:
                pass

    assert total_offenders <= total_allowed, (
        f"Expected at most {total_allowed} string concatenations (+=) in loops, "
        f"found {total_offenders}. Use list append and ''.join() instead."
    )
