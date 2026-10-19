import ast
import glob
import os
import pytest

# Allowlist for existing files that violate the print() rule
ALLOWLIST = {
    "geoai_cli.py",
    "humboldt.py",
    "install_requirements.py",
    "test_distance_issue.py",
    "dd2dms.py",
    "distance.py",
    "geocode.py",
}

class PrintChecker(ast.NodeVisitor):
    def __init__(self):
        self.illegal_prints = []
        self.in_main_guard = False
        self.in_cli_entry = False

    def visit_If(self, node):
        # Check for if __name__ == '__main__':
        is_main = False
        if isinstance(node.test, ast.Compare):
            if isinstance(node.test.left, ast.Name) and node.test.left.id == '__name__':
                if len(node.test.ops) == 1 and isinstance(node.test.ops[0], ast.Eq):
                    if len(node.test.comparators) == 1 and isinstance(node.test.comparators[0], ast.Constant) and node.test.comparators[0].value == '__main__':
                        is_main = True

        old_in_main = self.in_main_guard
        if is_main:
            self.in_main_guard = True

        self.generic_visit(node)

        self.in_main_guard = old_in_main

    def visit_FunctionDef(self, node):
        # Check for main or cli functions
        is_cli = node.name in ('main', 'cli')
        old_in_cli = self.in_cli_entry
        if is_cli:
            self.in_cli_entry = True

        self.generic_visit(node)

        self.in_cli_entry = old_in_cli

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == 'print':
            if not (self.in_main_guard or self.in_cli_entry):
                self.illegal_prints.append((node.lineno, node.col_offset))
        self.generic_visit(node)

def get_python_files():
    files = glob.glob("*.py") + glob.glob("plugins/*.py")
    return [f for f in files if not f.startswith("tests/") and not f.startswith("ast_test.py")]

@pytest.mark.parametrize("filepath", get_python_files())
def test_no_prints_outside_main_or_cli(filepath):
    filename = os.path.basename(filepath)
    if filename in ALLOWLIST:
        pytest.skip(f"{filename} is in the allowlist for illegal print() calls.")

    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source, filename=filepath)
    checker = PrintChecker()
    checker.visit(tree)

    assert not checker.illegal_prints, (
        f"Found {len(checker.illegal_prints)} illegal print() calls in {filepath}. "
        "Prints are only allowed inside `if __name__ == '__main__':` guards or CLI entry functions (main, cli)."
    )
