import ast
import glob
import pytest

# Allowlist for existing offenders: {"filename.py": count}
ALLOWLIST = {}

def test_del_statements_count():
    """
    Parses every top-level .py module and plugins/*.py with ast and counts 'del' statements.
    Fails if the total grows beyond the current count, with an allowlist for current offenders.
    """
    files = glob.glob("*.py") + glob.glob("plugins/*.py")

    current_offenders = {}
    total_found = 0

    for f in files:
        with open(f, "r", encoding="utf-8") as file:
            try:
                tree = ast.parse(file.read(), filename=f)
            except SyntaxError:
                continue

        count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Delete):
                count += 1

        if count > 0:
            current_offenders[f] = count
            total_found += count

    total_allowed = sum(ALLOWLIST.values())

    error_msg = f"Found {total_found} 'del' statements (allowed {total_allowed}). Offenders: {current_offenders}"
    assert total_found <= total_allowed, error_msg

    for f, count in current_offenders.items():
        allowed_count = ALLOWLIST.get(f, 0)
        assert count <= allowed_count, f"{f} has {count} 'del' statements, but only {allowed_count} are allowed."
