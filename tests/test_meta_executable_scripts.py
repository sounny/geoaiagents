import subprocess
import pytest

# Allowlist for files that start with a shebang but are not marked as executable in Git
ALLOWLIST = [
    "install_requirements.py"
]

def test_executable_scripts_have_executable_bit():
    """
    Ensure all tracked files that start with #! are marked as executable in Git.
    """
    try:
        output = subprocess.check_output(['git', 'ls-files', '-s'], text=True)
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Failed to run git ls-files: {e}")

    offenders = []

    for line in output.splitlines():
        parts = line.split('\t')
        if len(parts) != 2:
            continue

        metadata = parts[0].split()
        if len(metadata) < 1:
            continue

        mode = metadata[0]
        filename = parts[1]

        # Check if the file is tracked as non-executable (100644)
        if mode == '100644':
            if filename in ALLOWLIST:
                continue

            try:
                with open(filename, 'rb') as f:
                    if f.read(2) == b'#!':
                        offenders.append(filename)
            except Exception:
                # Ignore files that cannot be read (e.g. symlinks, directories, or missing files)
                pass

    assert not offenders, f"The following tracked files start with '#!' but are not marked as executable in git: {offenders}"
