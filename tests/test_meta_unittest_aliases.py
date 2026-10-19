import ast
import glob
import pytest

# Allowlist for existing files that use deprecated unittest aliases.
# Currently empty as no such offenders were found.
ALLOWLIST = set()

def test_no_deprecated_unittest_aliases():
    """
    Ensure no test_*.py files use deprecated unittest aliases like
    assertEquals, assertNotEquals, assertRegexpMatches, or failUnless.
    """
    deprecated_aliases = {
        'assertEquals',
        'assertNotEquals',
        'assertRegexpMatches',
        'failUnless'
    }

    offenders = []

    for filepath in glob.glob('tests/test_*.py'):
        if filepath in ALLOWLIST or filepath.endswith('test_meta_unittest_aliases.py'):
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read(), filename=filepath)
            except SyntaxError:
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr in deprecated_aliases:
                offenders.append(f"{filepath} uses {node.attr}")

    assert not offenders, "Found deprecated unittest aliases:\n" + "\n".join(offenders)
