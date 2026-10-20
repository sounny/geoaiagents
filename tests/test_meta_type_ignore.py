import os
import glob
import ast
import tokenize
import pytest

ALLOWED_OFFENDERS = {}

def get_python_files():
    files = glob.glob("*.py") + glob.glob("plugins/*.py")
    return [f for f in files if os.path.isfile(f)]

def test_type_ignore_count():
    files = get_python_files()
    total_count = 0
    actual_offenders = {}

    for filepath in files:
        # Just to ensure it can be parsed by ast
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
            ast.parse(source)

        file_count = 0
        with open(filepath, 'rb') as f:
            for token in tokenize.tokenize(f.readline):
                if token.type == tokenize.COMMENT and '# type: ignore' in token.string:
                    file_count += 1

        if file_count > 0:
            actual_offenders[filepath] = file_count
            total_count += file_count

    expected_total = sum(ALLOWED_OFFENDERS.values())

    # Assert total count hasn't grown
    assert total_count <= expected_total, f"Total '# type: ignore' count ({total_count}) exceeded allowed ({expected_total})"

    # Assert no new files have # type: ignore
    for filepath, count in actual_offenders.items():
        assert filepath in ALLOWED_OFFENDERS, f"File {filepath} has {count} '# type: ignore' comments but is not in the allowlist."
        assert count <= ALLOWED_OFFENDERS[filepath], f"File {filepath} has {count} '# type: ignore' comments, allowed is {ALLOWED_OFFENDERS[filepath]}."
