import ast
import glob
import pytest

# Maintain an allowlist of known offenders in the format "filename.py:lineno"
# Currently there are 0 offenders.
ALLOWLIST = ["file_loaders.py:25"]

def test_no_raise_new_exception_in_except_without_from():
    """
    AST-based meta-test to ensure that `raise` statements inside `except` handlers
    that raise a new exception also use the `from` keyword (e.g. `raise ValueError("...") from e`).
    """
    offenders = []

    files_to_check = glob.glob("*.py") + glob.glob("plugins/*.py")

    for filename in files_to_check:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                source = f.read()
            tree = ast.parse(source, filename=filename)
        except Exception:
            # Skip files that cannot be parsed (e.g., due to syntax errors or non-Python content)
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                # Walk the nodes inside the except handler body
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.Raise):
                        # exc is not None means it's raising a specific exception (not a bare raise)
                        # cause is None means there is no "from" clause
                        if subnode.exc is not None and subnode.cause is None:
                            offender_str = f"{filename}:{subnode.lineno}"
                            if offender_str not in ALLOWLIST:
                                offenders.append(offender_str)

    assert len(offenders) == 0, (
        "Found raise statements inside except handlers raising new exceptions without a 'from' clause:\n" +
        "\n".join(f"  - {off}" for off in offenders)
    )
