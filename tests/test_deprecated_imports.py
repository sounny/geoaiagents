import ast
import glob
import os
import pytest

# Deprecated modules we want to avoid
DEPRECATED_MODULES = {"imp", "distutils", "asynchat", "asyncore"}

# Allowlist for existing offenders: {filepath: {module_names}}
# We check if a file has an allowed deprecated module
ALLOWLIST = {
    # No known offenders currently. Add them here if needed.
    # "plugins/my_plugin.py": {"imp"}
}

def get_target_files():
    # Top-level .py files
    top_level_files = glob.glob("*.py")

    # Files in plugins/ directory
    plugin_files = glob.glob("plugins/*.py")

    return top_level_files + plugin_files

def check_for_deprecated_imports(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        source_code = f.read()

    try:
        tree = ast.parse(source_code, filename=filepath)
    except SyntaxError as e:
        # We don't want the test to fail if there's a syntax error in some other script,
        # but for top-level files it probably shouldn't have syntax errors anyway.
        # We'll just skip or raise it depending on preference. We'll raise it here to be strict.
        raise RuntimeError(f"Syntax error in {filepath}: {e}")

    violations = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                # alias.name could be 'imp' or 'distutils.core' etc.
                base_module = alias.name.split('.')[0]
                if base_module in DEPRECATED_MODULES:
                    violations.append((node.lineno, base_module, alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                base_module = node.module.split('.')[0]
                if base_module in DEPRECATED_MODULES:
                    violations.append((node.lineno, base_module, node.module))

    return violations

@pytest.mark.parametrize("filepath", get_target_files())
def test_no_deprecated_imports(filepath):
    """
    Test that the file does not import any of the deprecated modules:
    imp, distutils, asynchat, or asyncore.
    """
    violations = check_for_deprecated_imports(filepath)

    if not violations:
        return

    allowed_for_file = ALLOWLIST.get(filepath, set())

    unallowed_violations = []
    for lineno, base_module, full_import in violations:
        if base_module not in allowed_for_file:
            unallowed_violations.append(f"Line {lineno}: '{full_import}' (base '{base_module}')")

    if unallowed_violations:
        violations_str = "\n".join(unallowed_violations)
        pytest.fail(f"File {filepath} imports deprecated modules:\n{violations_str}")
