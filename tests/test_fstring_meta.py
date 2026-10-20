import ast
import glob
import os
import pytest

class FStringChecker(ast.NodeVisitor):
    def __init__(self, filepath):
        self.filepath = filepath
        self.offenders = []

    def visit_JoinedStr(self, node):
        has_formatted = any(isinstance(v, ast.FormattedValue) for v in node.values)
        if not has_formatted:
            self.offenders.append((self.filepath, getattr(node, 'lineno', -1)))
        self.generic_visit(node)

    def visit_FormattedValue(self, node):
        self.visit(node.value)
        # Deliberately do not visit node.format_spec to avoid flagging format specifiers as empty f-strings.

def get_python_files():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = glob.glob(os.path.join(root_dir, "*.py")) + glob.glob(os.path.join(root_dir, "plugins", "*.py"))

    # We want to use relative paths for the allowlist to be clean and stable
    rel_files = [os.path.relpath(f, root_dir) for f in files if os.path.isfile(f)]
    # Sort for deterministic test order
    return sorted(rel_files)

# Allowlist formatted as tuples of (filename, lineno)
ALLOWLIST = {
    ("install_requirements.py", 81),
}

@pytest.mark.parametrize("filepath", get_python_files())
def test_no_empty_fstrings(filepath):
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(root_dir, filepath)

    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()

    try:
        tree = ast.parse(content, filename=filepath)
    except SyntaxError:
        pytest.skip(f"Syntax error in {filepath}")

    checker = FStringChecker(filepath)
    checker.visit(tree)

    unallowed_offenders = []
    for off in checker.offenders:
        if off not in ALLOWLIST:
            unallowed_offenders.append(off)

    if unallowed_offenders:
        pytest.fail(f"Found f-strings with no {{}} placeholders: {unallowed_offenders}")
