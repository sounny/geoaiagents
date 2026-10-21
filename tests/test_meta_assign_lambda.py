import ast
import glob
import os
import pytest

def get_python_files():
    # Top-level .py files
    files = glob.glob("*.py")
    # plugins/*.py
    files.extend(glob.glob("plugins/*.py"))
    return sorted([f for f in files if os.path.isfile(f)])

ALLOWLIST = {
    # No existing offenders found based on the grep
}

class ScopeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.scope_stack = ['Module']
        self.offenders = []

    def visit_Module(self, node):
        # We start in 'Module' scope, push logic doesn't strictly need it as we init with it
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.scope_stack.append('FunctionDef')
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_AsyncFunctionDef(self, node):
        self.scope_stack.append('AsyncFunctionDef')
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_ClassDef(self, node):
        self.scope_stack.append('ClassDef')
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_Assign(self, node):
        if isinstance(node.value, ast.Lambda):
            current_scope = self.scope_stack[-1]
            if current_scope in ('Module', 'FunctionDef', 'AsyncFunctionDef'):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.offenders.append(target.id)
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        if isinstance(node.value, ast.Lambda):
            current_scope = self.scope_stack[-1]
            if current_scope in ('Module', 'FunctionDef', 'AsyncFunctionDef'):
                if isinstance(node.target, ast.Name):
                    self.offenders.append(node.target.id)
        self.generic_visit(node)


@pytest.mark.parametrize("filepath", get_python_files())
def test_no_lambda_assignment(filepath):
    """
    Ensure that we do not assign a lambda to a variable name at the module or function level.
    Use 'def' instead.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
        except SyntaxError:
            pytest.skip(f"SyntaxError when parsing {filepath}")

    visitor = ScopeVisitor()
    visitor.visit(tree)
    count = len(visitor.offenders)

    allowed = ALLOWLIST.get(filepath, 0)
    assert count <= allowed, (
        f"File {filepath} contains {count} lambda assignment(s) at module/function scope "
        f"(allowed: {allowed}). Please use 'def' to define functions instead."
    )
