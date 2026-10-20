import ast
import glob
import pytest

def test_no_new_nonlocal_statements():
    """
    Meta-test to ensure that top-level .py modules and plugins/*.py do not increase
    their usage of `nonlocal` statements beyond the current baseline.
    """
    # Current offenders allowlist mapping file path to number of nonlocal statements
    # Currently there are no offenders.
    allowlist = {}

    total_allowed = sum(allowlist.values())

    # Collect all top-level .py files and plugins/*.py files
    target_files = glob.glob("*.py") + glob.glob("plugins/*.py")

    total_nonlocal = 0
    file_counts = {}

    for file_path in target_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            tree = ast.parse(content, filename=file_path)
        except Exception as e:
            pytest.fail(f"Failed to parse {file_path}: {e}")

        count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Nonlocal):
                count += 1

        if count > 0:
            file_counts[file_path] = count
            total_nonlocal += count

    # Verify that no new offenders were introduced
    for file_path, count in file_counts.items():
        allowed_count = allowlist.get(file_path, 0)
        assert count <= allowed_count, (
            f"File {file_path} contains {count} nonlocal statement(s), "
            f"which exceeds the allowed baseline of {allowed_count}."
        )

    assert total_nonlocal <= total_allowed, (
        f"Total number of nonlocal statements ({total_nonlocal}) exceeds "
        f"the allowed baseline ({total_allowed})."
    )
