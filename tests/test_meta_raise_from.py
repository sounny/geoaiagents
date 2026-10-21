import ast
from pathlib import Path


class RaiseVisitor(ast.NodeVisitor):
    def __init__(self):
        self.in_except_handler = 0
        self.count = 0

    def visit_ExceptHandler(self, node):
        self.in_except_handler += 1
        self.generic_visit(node)
        self.in_except_handler -= 1

    def visit_Raise(self, node):
        if self.in_except_handler > 0:
            if node.exc is not None and isinstance(node.exc, ast.Call):
                if node.cause is None:
                    self.count += 1
        self.generic_visit(node)


def test_no_raise_call_without_from_inside_except():
    base_dir = Path(__file__).parent.parent

    # Collect all top-level .py modules and plugins/*.py
    py_files = list(base_dir.glob("*.py")) + list((base_dir / "plugins").glob("*.py"))

    allowlist = {"file_loaders.py"}

    total_count = 0

    for file_path in py_files:
        try:
            tree = ast.parse(
                file_path.read_text(encoding="utf-8"), filename=str(file_path)
            )
        except SyntaxError:
            continue

        visitor = RaiseVisitor()
        visitor.visit(tree)

        file_count = visitor.count

        if file_count > 0:
            assert (
                file_path.name in allowlist
            ), f"File {file_path.name} is not in the allowlist but contains raise X(...) inside except handler without 'from'."

        total_count += file_count

    assert (
        total_count <= 1
    ), f"Total count of raise X(...) inside except without 'from' grew to {total_count}, expected <= 1"
