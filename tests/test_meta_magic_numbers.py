import ast
import glob
import os
import pytest

EXPECTED_MAGIC_NUMBERS = {
    'dd2dms.py': 2,
    'distance.py': 1,
    'geoai_cli.py': 1,
    'humboldt.py': 1,
    'validation.py': 4,
    'webchat.py': 1,
}

class MagicNumberVisitor(ast.NodeVisitor):
    def __init__(self):
        self.in_function = 0
        self.count = 0

    def visit_FunctionDef(self, node):
        self.in_function += 1
        self.generic_visit(node)
        self.in_function -= 1

    def visit_AsyncFunctionDef(self, node):
        self.in_function += 1
        self.generic_visit(node)
        self.in_function -= 1

    def visit_Compare(self, node):
        if self.in_function > 0:
            for expr in [node.left] + node.comparators:
                self.check_expr(expr)
        self.generic_visit(node)

    def check_expr(self, expr):
        if isinstance(expr, ast.Constant):
            if isinstance(expr.value, (int, float, complex)) and not isinstance(expr.value, bool):
                if expr.value not in {-1, 0, 1, 2}:
                    self.count += 1
        elif isinstance(expr, ast.UnaryOp) and isinstance(expr.op, ast.USub):
            if isinstance(expr.operand, ast.Constant):
                if isinstance(expr.operand.value, (int, float, complex)) and not isinstance(expr.operand.value, bool):
                    val = -expr.operand.value
                    if val not in {-1, 0, 1, 2}:
                        self.count += 1

def count_magic_numbers(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    tree = ast.parse(content)
    visitor = MagicNumberVisitor()
    visitor.visit(tree)
    return visitor.count

def get_files_to_check():
    files = glob.glob("*.py") + glob.glob("plugins/*.py")
    return sorted(files)

@pytest.mark.parametrize("filepath", get_files_to_check())
def test_no_new_magic_numbers(filepath):
    count = count_magic_numbers(filepath)
    expected = EXPECTED_MAGIC_NUMBERS.get(filepath, 0)

    assert count <= expected, f"File {filepath} has {count} magic numbers in comparisons inside functions, but expected at most {expected}."
