import ast
import glob
import os
import pytest

# Add any known offenders to this allowlist.
# E.g., 'bad_file.py' or 'plugins/bad_plugin.py'
ALLOWLIST = set()

def get_target_files():
    files = glob.glob('*.py') + glob.glob('plugins/*.py')
    # Filter out test files and files in the allowlist
    files = [f for f in files if f not in ALLOWLIST and not os.path.basename(f).startswith('test_')]
    return files

@pytest.mark.parametrize("filepath", get_target_files())
def test_no_mktemp_calls(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    try:
        tree = ast.parse(content, filename=filepath)
    except SyntaxError as e:
        pytest.fail(f"Syntax error in {filepath}: {e}")

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Check for tempfile.mktemp()
            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name) and node.func.value.id == 'tempfile' and node.func.attr == 'mktemp':
                    pytest.fail(f"Found tempfile.mktemp() call in {filepath} at line {node.lineno}. Use mkstemp or NamedTemporaryFile instead.")
            # Check for mktemp() directly if imported via `from tempfile import mktemp`
            elif isinstance(node.func, ast.Name) and node.func.id == 'mktemp':
                # Note: This is a bit aggressive as someone could name a local function 'mktemp',
                # but it's a good safety check for the specific requirement.
                pytest.fail(f"Found mktemp() call in {filepath} at line {node.lineno}. Use mkstemp or NamedTemporaryFile instead.")
