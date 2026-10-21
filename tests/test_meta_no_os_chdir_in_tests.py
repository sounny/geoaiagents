import ast
import pytest
from pathlib import Path

# Provide a list of scripts that might be allowed to use os.chdir in tests
# Add to this allowlist as necessary
ALLOWLIST = []

def get_test_files():
    return list(Path('tests').glob('test_*.py'))

@pytest.mark.parametrize("filepath", get_test_files(), ids=lambda p: str(p))
def test_no_os_chdir_in_tests(filepath):
    """
    Ensure no test files call os.chdir()
    to avoid unexpected side effects in the running test suite.
    """
    if str(filepath) in ALLOWLIST:
        pytest.skip(reason=f"File {filepath} is in the allowlist for os.chdir() in tests")

    content = filepath.read_text(encoding='utf-8')
    try:
        tree = ast.parse(content, filename=str(filepath))
    except SyntaxError as e:
        pytest.fail(f"Syntax error in {filepath}: {e}")

    class OsChdirVisitor(ast.NodeVisitor):
        def __init__(self):
            self.violations = []

        def visit_Call(self, node):
            # Check for os.chdir()
            if isinstance(node.func, ast.Attribute):
                if getattr(node.func.value, 'id', None) == 'os':
                    if node.func.attr == 'chdir':
                        self.violations.append(node.lineno)
            self.generic_visit(node)

    visitor = OsChdirVisitor()
    visitor.visit(tree)

    if visitor.violations:
        lines_str = ', '.join(map(str, visitor.violations))
        pytest.fail(f"Found os.chdir() call(s) in {filepath} on line(s): {lines_str}. Use of os.chdir() in tests is forbidden. Use monkeypatch.chdir or tmp_path.")
