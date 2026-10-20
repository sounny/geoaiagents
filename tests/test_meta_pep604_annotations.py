import ast
import glob
import sys
import pytest

ALLOWLIST = {
    "webchat.py"
}

class AnnotationVisitor(ast.NodeVisitor):
    def __init__(self):
        self.in_annotation = False
        self.found_bitor = False
        self.has_future_annotations = False

    def visit_ImportFrom(self, node):
        if node.module == "__future__":
            for alias in node.names:
                if alias.name == "annotations":
                    self.has_future_annotations = True
        self.generic_visit(node)

    def check_annotation(self, node):
        if node:
            old = self.in_annotation
            self.in_annotation = True
            self.visit(node)
            self.in_annotation = old

    def visit_AnnAssign(self, node):
        self.visit(node.target)
        self.check_annotation(node.annotation)
        if node.value:
            self.visit(node.value)

    def visit_arg(self, node):
        self.check_annotation(node.annotation)

    def visit_FunctionDef(self, node):
        for dec in node.decorator_list:
            self.visit(dec)
        self.visit(node.args)
        self.check_annotation(node.returns)
        for stmt in node.body:
            self.visit(stmt)

    def visit_AsyncFunctionDef(self, node):
        for dec in node.decorator_list:
            self.visit(dec)
        self.visit(node.args)
        self.check_annotation(node.returns)
        for stmt in node.body:
            self.visit(stmt)

    def visit_BinOp(self, node):
        if self.in_annotation and isinstance(node.op, ast.BitOr):
            self.found_bitor = True
        self.generic_visit(node)

@pytest.mark.skipif(sys.version_info >= (3, 10), reason="PEP 604 is supported natively in Python 3.10+")
def test_pep604_annotations_require_future_import():
    files = glob.glob("*.py") + glob.glob("plugins/*.py")
    offenders = []

    for filepath in files:
        if filepath in ALLOWLIST:
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        try:
            tree = ast.parse(content)
        except SyntaxError:
            continue

        visitor = AnnotationVisitor()
        visitor.visit(tree)

        if visitor.found_bitor and not visitor.has_future_annotations:
            offenders.append(filepath)

    assert not offenders, (
        f"The following files use PEP 604 (X | Y) union syntax in annotations "
        f"but are missing 'from __future__ import annotations': {offenders}"
    )
