import ast
import glob
import os

ALLOWLIST = {}

class ListSetCompVisitor(ast.NodeVisitor):
    def __init__(self):
        self.count = 0

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id in {"list", "set"}:
            if len(node.args) == 1 and isinstance(node.args[0], ast.ListComp):
                self.count += 1
        self.generic_visit(node)

def test_meta_no_list_set_comprehension():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = glob.glob(os.path.join(root_dir, "*.py")) + glob.glob(os.path.join(root_dir, "plugins", "*.py"))

    total_offenders = 0
    total_allowed = sum(ALLOWLIST.values())

    for f in files:
        filename = os.path.basename(f)
        if filename.startswith("test_") or filename.startswith("conftest"):
            continue
        with open(f, "r", encoding="utf-8") as file:
            try:
                tree = ast.parse(file.read(), filename=f)
                v = ListSetCompVisitor()
                v.visit(tree)
                total_offenders += v.count
            except Exception:
                pass

    assert total_offenders <= total_allowed, (
        f"Expected at most {total_allowed} calls to list() or set() wrapping a list comprehension, "
        f"found {total_offenders}. Pass a generator expression instead."
    )
