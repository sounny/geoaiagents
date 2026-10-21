import ast
import glob
import os
import pytest

# Allowlist for existing offenders that directly modify os.environ in tests
ALLOWLIST = ["test_webchat_config.py"]

class OsEnvironTestVisitor(ast.NodeVisitor):
    def __init__(self):
        self.violations = []

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Subscript):
                if isinstance(target.value, ast.Attribute):
                    if isinstance(target.value.value, ast.Name) and target.value.value.id == "os" and target.value.attr == "environ":
                        self.violations.append(node.lineno)
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == "update" and isinstance(node.func.value, ast.Attribute):
                if isinstance(node.func.value.value, ast.Name) and node.func.value.value.id == "os" and node.func.value.attr == "environ":
                    self.violations.append(node.lineno)
            elif node.func.attr == "putenv" and isinstance(node.func.value, ast.Name) and node.func.value.id == "os":
                self.violations.append(node.lineno)
            elif node.func.attr == "setdefault" and isinstance(node.func.value, ast.Attribute):
                if isinstance(node.func.value.value, ast.Name) and node.func.value.value.id == "os" and node.func.value.attr == "environ":
                    self.violations.append(node.lineno)
            elif node.func.attr == "pop" and isinstance(node.func.value, ast.Attribute):
                if isinstance(node.func.value.value, ast.Name) and node.func.value.value.id == "os" and node.func.value.attr == "environ":
                    self.violations.append(node.lineno)
        self.generic_visit(node)

    def visit_Delete(self, node):
        for target in node.targets:
            if isinstance(target, ast.Subscript):
                if isinstance(target.value, ast.Attribute):
                    if isinstance(target.value.value, ast.Name) and target.value.value.id == "os" and target.value.attr == "environ":
                        self.violations.append(node.lineno)
        self.generic_visit(node)


def test_no_direct_os_environ_writes_in_tests():
    """
    Ensure no direct writes to os.environ in tests (e.g., os.environ["KEY"] = "val").
    Use monkeypatch.setenv instead.
    """
    files_to_check = glob.glob("tests/test_*.py")
    all_violations = {}

    for filepath in files_to_check:
        basename = os.path.basename(filepath)
        if basename in ALLOWLIST or filepath in ALLOWLIST:
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=filepath)
            except SyntaxError:
                continue

        visitor = OsEnvironTestVisitor()
        visitor.visit(tree)

        if visitor.violations:
            all_violations[filepath] = visitor.violations

    assert not all_violations, f"Found direct os.environ modifications in tests (use monkeypatch.setenv): {all_violations}"
