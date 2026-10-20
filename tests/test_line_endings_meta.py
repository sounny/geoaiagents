import subprocess
import os

ALLOWLIST = set()

def test_no_crlf_line_endings():
    """Ensure that no tracked .py files contain \\r\\n line endings."""
    try:
        output = subprocess.check_output(['git', 'ls-files'], text=True)
    except subprocess.CalledProcessError:
        # If we can't run git ls-files (e.g. not a git repo), just skip
        return

    files = output.splitlines()
    offenders = []

    for file_path in files:
        if not file_path.endswith('.py'):
            continue

        # Exclude .git and virtualenv folders
        if '.git' in file_path.split(os.sep) or 'virtualenv' in file_path.split(os.sep):
            continue

        if not os.path.isfile(file_path):
            continue

        if file_path in ALLOWLIST:
            continue

        with open(file_path, 'rb') as f:
            if b'\r\n' in f.read():
                offenders.append(file_path)

    assert not offenders, f"The following files contain \\r\\n line endings: {offenders}"
