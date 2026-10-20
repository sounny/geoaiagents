import ast
import glob

class ReturnVisitor(ast.NodeVisitor):
    def __init__(self):
        self.offenders = []

    def visit_FunctionDef(self, node):
        pass

    def visit_AsyncFunctionDef(self, node):
        pass

    def visit_ClassDef(self, node):
        pass

    def visit_Return(self, node):
        if node.value is not None:
            if hasattr(ast, 'Constant') and isinstance(node.value, ast.Constant) and node.value.value is None:
                pass
            # For python < 3.8
            elif hasattr(ast, 'NameConstant') and isinstance(node.value, getattr(ast, 'NameConstant')) and node.value.value is None:
                pass
            else:
                self.offenders.append(node.lineno)

def check_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read(), filename=filepath)

    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == '__init__':
            visitor = ReturnVisitor()
            for child in node.body:
                visitor.visit(child)
            offenders.extend(visitor.offenders)
    return offenders

def test_meta_init_no_return_value():
    files = glob.glob("*.py") + glob.glob("plugins/*.py")
    all_offenders = {}

    allowlist = {
        # 'filename.py': [line_numbers]
    }

    for f in files:
        res = check_file(f)
        filtered_res = [line for line in res if line not in allowlist.get(f, [])]
        if filtered_res:
            all_offenders[f] = filtered_res

    assert not all_offenders, f"__init__ methods should not return a non-None value: {all_offenders}"
