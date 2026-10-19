import ast
import glob
import os
import pytest

# Allowlist for current offenders
# E.g., ALLOWLIST = ["humboldt.py", "plugins/some_plugin.py"]
ALLOWLIST = []

class OsEnvironVisitor(ast.NodeVisitor):
    def __init__(self):
        self.in_main = False
        self.violations = []

    def visit_If(self, node):
        is_main = False
        if isinstance(node.test, ast.Compare):
            if isinstance(node.test.left, ast.Name) and node.test.left.id == "__name__":
                if len(node.test.comparators) == 1 and isinstance(node.test.comparators[0], ast.Constant):
                    if node.test.comparators[0].value == "__main__":
                        is_main = True

        old_in_main = self.in_main
        if is_main:
            self.in_main = True

        self.generic_visit(node)
        self.in_main = old_in_main

    def visit_Assign(self, node):
        if not self.in_main:
            for target in node.targets:
                # check for os.environ[...]
                if isinstance(target, ast.Subscript):
                    if isinstance(target.value, ast.Attribute):
                        if isinstance(target.value.value, ast.Name) and target.value.value.id == "os" and target.value.attr == "environ":
                            self.violations.append(node.lineno)
        self.generic_visit(node)

    def visit_Call(self, node):
        if not self.in_main:
            if isinstance(node.func, ast.Attribute):
                # os.environ.update(...)
                if node.func.attr == "update" and isinstance(node.func.value, ast.Attribute):
                    if isinstance(node.func.value.value, ast.Name) and node.func.value.value.id == "os" and node.func.value.attr == "environ":
                        self.violations.append(node.lineno)
                # os.putenv(...)
                elif node.func.attr == "putenv" and isinstance(node.func.value, ast.Name) and node.func.value.id == "os":
                    self.violations.append(node.lineno)
        self.generic_visit(node)


def test_no_os_environ_modifications_outside_main():
    files_to_check = glob.glob("*.py") + glob.glob("plugins/*.py")
    all_violations = {}

    for filepath in files_to_check:
        if filepath in ALLOWLIST or os.path.basename(filepath) in ALLOWLIST:
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()

        try:
            tree = ast.parse(source, filename=filepath)
        except SyntaxError:
            continue

        visitor = OsEnvironVisitor()
        visitor.visit(tree)

        if visitor.violations:
            all_violations[filepath] = visitor.violations

    assert not all_violations, f"Found os.environ/os.putenv modifications outside __main__ guard: {all_violations}"
