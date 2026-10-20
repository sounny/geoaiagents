import ast
import glob
from pathlib import Path

# Functions that currently exceed 6 return statements
EXPECTED_OFFENDERS = {
    "geoai_cli.py::_run_tool_command",
}

class ReturnCountVisitor(ast.NodeVisitor):
    def __init__(self):
        self.returns = 0

    def visit_Return(self, node):
        self.returns += 1

    def visit_FunctionDef(self, node):
        # Do not recurse into nested functions
        pass

    def visit_AsyncFunctionDef(self, node):
        # Do not recurse into nested functions
        pass

    def visit_ClassDef(self, node):
        # Do not recurse into nested classes
        pass

def count_returns(func_node):
    visitor = ReturnCountVisitor()
    for child in func_node.body:
        visitor.visit(child)
    return visitor.returns

def test_meta_function_returns_limit():
    """
    Top-level Python modules and plugins (plugins/*.py) must not contain
    functions with more than six return statements.
    This is enforced by an AST-based pytest meta-test using an allowlist for existing offenders.
    """
    root_dir = Path(__file__).parent.parent
    files = glob.glob(str(root_dir / '*.py')) + glob.glob(str(root_dir / 'plugins' / '*.py'))

    # Exclude tests just in case, though the prompt says "top-level .py module and plugins/*.py".
    # Since we are iterating over '*.py', test files are not at the top-level except maybe `test_*.py` if they are top-level,
    # but tests are usually in tests/. The prompt says "parses every top-level .py module and plugins/*.py".

    offenders = set()

    for filepath in files:
        path_obj = Path(filepath)
        # Verify it's either top-level or in plugins/
        # Usually it matches by glob above.
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read(), filename=filepath)
            except SyntaxError:
                continue

        rel_path = path_obj.relative_to(root_dir).as_posix()

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                num_returns = count_returns(node)
                if num_returns > 6:
                    offenders.add(f"{rel_path}::{node.name}")

    new_offenders = offenders - EXPECTED_OFFENDERS

    assert not new_offenders, f"Found functions with more than 6 return statements: {new_offenders}"

    assert len(offenders) <= len(EXPECTED_OFFENDERS), \
        f"Total functions with >6 returns ({len(offenders)}) exceeds baseline ({len(EXPECTED_OFFENDERS)})"
