import ast
import pytest
from pathlib import Path

# Provide a list of scripts that might be allowed to use os.chdir
# Add to this allowlist as necessary
ALLOWLIST = []

def get_python_files():
    root_files = list(Path('.').glob('*.py'))
    plugin_files = list(Path('plugins').glob('*.py'))
    return root_files + plugin_files

@pytest.mark.parametrize("filepath", get_python_files(), ids=lambda p: str(p))
def test_no_os_chdir(filepath):
    """
    Ensure no top-level Python modules or plugin modules call os.chdir()
    to avoid unexpected side effects in the running process.
    """
    if str(filepath) in ALLOWLIST:
        pytest.skip(reason=f"File {filepath} is in the allowlist for os.chdir()")

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
                if isinstance(node.func.value, ast.Name) and node.func.value.id == 'os':
                    if node.func.attr == 'chdir':
                        self.violations.append(node.lineno)
            self.generic_visit(node)

    visitor = OsChdirVisitor()
    visitor.visit(tree)

    if visitor.violations:
        lines_str = ', '.join(map(str, visitor.violations))
        pytest.fail(f"Found os.chdir() call(s) in {filepath} on line(s): {lines_str}. Use of os.chdir() is forbidden.")
