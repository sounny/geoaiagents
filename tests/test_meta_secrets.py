import ast
import os
import pytest

# Paths to search for python files
ROOT_DIR = "."
PLUGINS_DIR = "plugins"

# Common secret prefixes to search for
SECRET_PREFIXES = ('AKIA', 'AIza', 'sk-', 'ghp_', 'xox')

# Allowlist: dictionary mapping filepath to a list of allowed secret strings.
# Example: {'geocode.py': ['sk-1234567890abcdefg']}
ALLOWLIST = {}

def get_python_files():
    """Yields all top-level .py files and .py files in plugins/."""
    # Top-level .py files
    for entry in os.listdir(ROOT_DIR):
        if entry.endswith('.py') and os.path.isfile(entry):
            yield entry

    # plugins/ .py files
    if os.path.exists(PLUGINS_DIR):
        for entry in os.listdir(PLUGINS_DIR):
            if entry.endswith('.py'):
                filepath = os.path.join(PLUGINS_DIR, entry)
                if os.path.isfile(filepath):
                    yield filepath

def test_no_hardcoded_secrets():
    """
    Parses every top-level .py module and plugins/*.py with ast and fails
    on string literals matching common secret prefixes longer than 16 characters,
    with an allowlist for current offenders.
    """
    offenders = []

    for filepath in get_python_files():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content, filename=filepath)
        except Exception as e:
            pytest.fail(f"Could not parse {filepath}: {e}")

        allowed_in_file = ALLOWLIST.get(filepath, [])

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                val = node.value
                if val.startswith(SECRET_PREFIXES) and len(val) > 16:
                    if val not in allowed_in_file:
                        offenders.append(f"File {filepath} contains a potential secret starting with {val[:4]}... (length: {len(val)})")

    if offenders:
        pytest.fail("Found potential hardcoded secrets:\n" + "\n".join(offenders))
