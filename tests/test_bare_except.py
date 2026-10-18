import ast
import glob
import os

def test_no_bare_excepts():
    """
    Parses every top-level .py module and plugins/*.py with ast
    and fails on any bare "except:" clause, with an allowlist for current offenders.
    """
    # Find all target files relative to the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = glob.glob(os.path.join(project_root, '*.py')) + glob.glob(os.path.join(project_root, 'plugins', '*.py'))

    # Allowlist of existing bare excepts
    # Format: {'filename.py': [line_number1, line_number2]}
    allowlist = {}

    errors = []

    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            source = f.read()

        try:
            tree = ast.parse(source, filename=file)
        except SyntaxError as e:
            errors.append(f"Syntax error in {file}: {e}")
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    # It's a bare except
                    if file in allowlist and node.lineno in allowlist[file]:
                        continue
                    errors.append(f"{file}:{node.lineno}: bare except found. Catch a specific exception instead.")

    assert not errors, "\n".join(errors)
