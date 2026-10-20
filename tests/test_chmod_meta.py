import ast
import glob
import os
import pytest

ALLOWLIST = []

class ChmodVisitor(ast.NodeVisitor):
    def __init__(self):
        self.violations = []

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            if node.func.value.id == "os" and node.func.attr == "chmod":
                if len(node.args) >= 2:
                    mode_arg = node.args[1]
                else:
                    mode_arg = None
                    for keyword in node.keywords:
                        if keyword.arg == "mode":
                            mode_arg = keyword.value
                            break
                if mode_arg is not None:
                    if isinstance(mode_arg, ast.Constant):
                        if mode_arg.value in (0o777, 0o666):
                            self.violations.append(node.lineno)
        self.generic_visit(node)


def get_files_to_check():
    files = glob.glob("*.py") + glob.glob("plugins/*.py")
    # Filter to only actual files, skip directories if any
    files = [f for f in files if os.path.isfile(f)]
    return files

@pytest.mark.parametrize("filepath", get_files_to_check())
def test_no_insecure_chmod(filepath):
    if filepath in ALLOWLIST:
        return

    with open(filepath, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=filepath)

    visitor = ChmodVisitor()
    visitor.visit(tree)

    if visitor.violations:
        lines_str = ", ".join(map(str, visitor.violations))
        pytest.fail(f"{filepath} contains os.chmod calls with mode 0o777 or 0o666 on lines: {lines_str}. Use a more secure mode.")
