import ast
import glob
import pytest

ALLOWLIST = set()

class FinallyBlockVisitor(ast.NodeVisitor):
    def __init__(self):
        self.blocks = []
        self.offenders = []

    def visit_Try(self, node):
        for stmt in node.body:
            self.visit(stmt)
        for handler in node.handlers:
            self.visit(handler)
        for stmt in node.orelse:
            self.visit(stmt)

        self.blocks.append('finally')
        for stmt in node.finalbody:
            self.visit(stmt)
        self.blocks.pop()

    def visit_TryStar(self, node):
        for stmt in node.body:
            self.visit(stmt)
        for handler in node.handlers:
            self.visit(handler)
        for stmt in node.orelse:
            self.visit(stmt)

        self.blocks.append('finally')
        for stmt in node.finalbody:
            self.visit(stmt)
        self.blocks.pop()

    def visit_For(self, node):
        self.blocks.append('loop')
        self.generic_visit(node)
        self.blocks.pop()

    def visit_AsyncFor(self, node):
        self.blocks.append('loop')
        self.generic_visit(node)
        self.blocks.pop()

    def visit_While(self, node):
        self.blocks.append('loop')
        self.generic_visit(node)
        self.blocks.pop()

    def visit_FunctionDef(self, node):
        self.blocks.append('function')
        self.generic_visit(node)
        self.blocks.pop()

    def visit_AsyncFunctionDef(self, node):
        self.blocks.append('function')
        self.generic_visit(node)
        self.blocks.pop()

    def _check_flow_control(self, node, node_type):
        target = 'function' if node_type == 'return' else 'loop'
        for block in reversed(self.blocks):
            if block == target:
                break
            if block == 'finally':
                self.offenders.append(node)
                break

    def visit_Return(self, node):
        self._check_flow_control(node, 'return')
        self.generic_visit(node)

    def visit_Break(self, node):
        self._check_flow_control(node, 'break')
        self.generic_visit(node)

    def visit_Continue(self, node):
        self._check_flow_control(node, 'continue')
        self.generic_visit(node)

def test_no_return_break_continue_in_finally():
    files_to_check = glob.glob("*.py") + glob.glob("plugins/*.py")

    all_offenders = []

    for filename in files_to_check:
        if filename in ALLOWLIST:
            continue

        try:
            with open(filename, "r", encoding="utf-8") as f:
                code = f.read()
            tree = ast.parse(code, filename=filename)
        except Exception as e:
            pytest.fail(f"Could not parse {filename}: {e}")

        visitor = FinallyBlockVisitor()
        visitor.visit(tree)

        for node in visitor.offenders:
            all_offenders.append(f"{filename}:{node.lineno} ({type(node).__name__})")

    if all_offenders:
        pytest.fail(f"Found return/break/continue inside finally blocks:\n" + "\n".join(all_offenders))
