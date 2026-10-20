import ast
import glob
from pathlib import Path

class FixtureVisitor(ast.NodeVisitor):
    def __init__(self):
        self.returns = []
        self.yields = []

    def visit_Return(self, node):
        self.returns.append(node)
        self.generic_visit(node)

    def visit_Yield(self, node):
        self.yields.append(node)
        self.generic_visit(node)

    def visit_YieldFrom(self, node):
        self.yields.append(node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        # Do not recurse into nested functions
        pass

    def visit_AsyncFunctionDef(self, node):
        # Do not recurse into nested async functions
        pass

    def visit_ClassDef(self, node):
        # Do not recurse into nested classes
        pass


def check_fixture(node):
    visitor = FixtureVisitor()
    # Manually visit the body of the function so we don't skip it due to visit_FunctionDef
    for stmt in node.body:
        visitor.visit(stmt)
    return visitor.returns, visitor.yields


def test_no_bare_return_fixtures():
    """
    Test files (tests/test_*.py) must not contain fixture functions whose only return
    is a bare "return None" or "return" with no yield.
    This is enforced by parsing every tests/test_*.py file with ast.
    """
    offenders = set()
    project_root = Path(__file__).parent.parent
    for file in glob.glob(str(project_root / 'tests' / 'test_*.py')):
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()

        try:
            tree = ast.parse(content, filename=file)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                is_fixture = False
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id == 'fixture':
                        is_fixture = True
                    elif isinstance(decorator, ast.Attribute) and getattr(decorator.value, 'id', '') == 'pytest' and decorator.attr == 'fixture':
                        is_fixture = True
                    elif isinstance(decorator, ast.Call):
                        func = decorator.func
                        if isinstance(func, ast.Name) and func.id == 'fixture':
                            is_fixture = True
                        elif isinstance(func, ast.Attribute) and getattr(func.value, 'id', '') == 'pytest' and func.attr == 'fixture':
                            is_fixture = True

                if is_fixture:
                    returns, yields = check_fixture(node)

                    if not yields:
                        if not returns:
                            offenders.add(f"{Path(file).name}::{node.name}")
                        else:
                            all_none_or_bare = all(r.value is None or (isinstance(r.value, ast.Constant) and r.value.value is None) for r in returns)
                            if all_none_or_bare:
                                offenders.add(f"{Path(file).name}::{node.name}")

    allowlist = set([
        # Add existing offenders here if needed in the future
    ])

    new_offenders = offenders - allowlist
    assert not new_offenders, f"Found fixtures whose only return is a bare 'return None' or 'return' with no yield: {sorted(list(new_offenders))}"
