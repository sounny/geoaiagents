import ast
import glob
import os
import pytest

def test_no_sys_exit_outside_main():
    """
    Ensure no top-level .py module or plugins/*.py calls sys.exit(), exit(),
    or quit() outside an `if __name__ == "__main__":` block or CLI entry function.
    """
    # Allowlist of current offenders to keep production code unchanged
    allowlist = {
        "humboldt.py",
    }

    files_to_check = glob.glob("*.py") + glob.glob("plugins/*.py")

    class ExitVisitor(ast.NodeVisitor):
        def __init__(self):
            self.in_main_block = False
            self.in_cli_func = False
            self.bad_exits = []

        def visit_If(self, node):
            # Check if this is an `if __name__ == "__main__":` block
            is_main_block = False
            if isinstance(node.test, ast.Compare):
                if len(node.test.ops) == 1 and isinstance(node.test.ops[0], ast.Eq):
                    left = node.test.left
                    right = node.test.comparators[0]
                    if isinstance(left, ast.Name) and left.id == "__name__":
                        if isinstance(right, ast.Constant) and right.value == "__main__":
                            is_main_block = True
                    elif isinstance(right, ast.Name) and right.id == "__name__":
                        if isinstance(left, ast.Constant) and left.value == "__main__":
                            is_main_block = True

            old_in_main = self.in_main_block

            if is_main_block:
                self.in_main_block = True
                for stmt in node.body:
                    self.visit(stmt)
                self.in_main_block = old_in_main

                for stmt in node.orelse:
                    self.visit(stmt)
            else:
                self.generic_visit(node)

        def visit_FunctionDef(self, node):
            old_in_cli = self.in_cli_func
            # Consider functions with 'main' or 'cli' in their name as CLI entry functions
            if "main" in node.name.lower() or "cli" in node.name.lower():
                self.in_cli_func = True

            self.generic_visit(node)
            self.in_cli_func = old_in_cli

        def visit_Call(self, node):
            is_exit = False
            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "sys" and node.func.attr == "exit":
                    is_exit = True
            elif isinstance(node.func, ast.Name):
                if node.func.id in ("exit", "quit"):
                    is_exit = True

            if is_exit:
                if not self.in_main_block and not self.in_cli_func:
                    self.bad_exits.append(node.lineno)

            self.generic_visit(node)

    for filepath in files_to_check:
        basename = os.path.basename(filepath)
        if basename in allowlist:
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=filepath)
            except SyntaxError:
                continue

        visitor = ExitVisitor()
        visitor.visit(tree)

        if visitor.bad_exits:
            pytest.fail(f"File {filepath} contains sys.exit(), exit(), or quit() calls outside __main__ guard or CLI entry function at lines: {visitor.bad_exits}")
