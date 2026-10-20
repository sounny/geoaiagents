import ast
import glob

ALLOWLIST = [
    # Allowlist of existing offenders
]

def test_no_assert_false_outside_tests():
    """
    Ensure no `assert False` statements are used outside test files.
    """
    files = glob.glob("*.py") + glob.glob("plugins/*.py")
    offenders = []

    for filepath in files:
        if filepath.startswith("test_") or "conftest" in filepath:
            continue

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            continue

        try:
            tree = ast.parse(content, filename=filepath)
        except Exception:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Assert):
                # Check for `assert False`
                if isinstance(node.test, ast.Constant) and node.test.value is False:
                    offenders.append(filepath)
                    break
                elif isinstance(node.test, ast.Name) and node.test.id == 'False':
                    offenders.append(filepath)
                    break

    new_offenders = [f for f in offenders if f not in ALLOWLIST]
    assert not new_offenders, f"Found `assert False` outside of tests in: {new_offenders}"
