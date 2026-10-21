import os
import subprocess
import pytest

# Allowlist of files that are permitted to be larger than 1 MB.
# Add the exact relative path of the file (as tracked by git) to this list.
ALLOWLIST = set()

MAX_SIZE_BYTES = 1048576  # 1 MB

def test_file_sizes_under_1mb():
    try:
        # Get all files tracked by git
        output = subprocess.check_output(
            ['git', 'ls-files'],
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
    except subprocess.CalledProcessError as e:
        pytest.skip(reason=f"Failed to run git ls-files: {e.output}")
        return

    tracked_files = output.strip().split('\n')

    oversized_files = []

    for filepath in tracked_files:
        if not filepath:
            continue

        if not os.path.exists(filepath):
            # File is tracked by git but missing from working directory
            continue

        if filepath in ALLOWLIST:
            continue

        size = os.path.getsize(filepath)
        if size > MAX_SIZE_BYTES:
            oversized_files.append((filepath, size))

    assert not oversized_files, (
        f"The following files exceed 1 MB: {oversized_files}. "
        "Please reduce their size or add them to the ALLOWLIST in tests/test_meta_file_size.py."
    )
