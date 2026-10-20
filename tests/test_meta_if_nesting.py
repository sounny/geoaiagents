import ast
import glob
import pytest
from pathlib import Path

# Allowlist mapping filepath to current count of `if` statements nested > 4 levels
ALLOWLIST = {
    'file_loaders.py': 1,
}

class IfNestingVisitor(ast.NodeVisitor):
    def __init__(self):
        self.nesting_level = 0
        self.offending_ifs = 0

    def visit_If(self, node):
        self.nesting_level += 1
        if self.nesting_level > 4:
            self.offending_ifs += 1

        self.generic_visit(node)

        self.nesting_level -= 1

def check_file(filepath: Path) -> int:
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        pytest.fail(f"Could not read {filepath}: {e}")

    try:
        tree = ast.parse(content, filename=str(filepath))
    except Exception as e:
        pytest.fail(f"Could not parse {filepath}: {e}")

    visitor = IfNestingVisitor()
    visitor.visit(tree)
    return visitor.offending_ifs

def test_meta_if_nesting():
    """
    Ensure that top-level .py modules and plugins/*.py do not increase
    their count of `if` statements nested more than four levels deep.
    """
    top_level_files = list(Path('.').glob('*.py'))
    plugin_files = list(Path('plugins').glob('*.py'))

    files_to_check = top_level_files + plugin_files

    total_offenders = 0
    errors = []

    for filepath in files_to_check:
        # Skip some standard build/setup/test-helper scripts if necessary, but typical meta tests just run on these.
        if filepath.name.startswith('find_nested_ifs') or filepath.name == 'install_requirements.py' or filepath.name == 'setup.py':
             # Actually let's check everything except our temp script
             if filepath.name == 'find_nested_ifs.py':
                 continue

        count = check_file(filepath)
        str_path = str(filepath).replace('\\', '/')

        allowed_count = ALLOWLIST.get(str_path, 0)

        if count > allowed_count:
            errors.append(f"{str_path}: found {count} deeply nested if statements (allowed: {allowed_count})")

    if errors:
        pytest.fail("\n".join(errors))
