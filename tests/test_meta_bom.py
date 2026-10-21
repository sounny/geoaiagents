import subprocess
from pathlib import Path

ALLOWLIST = []

def test_no_utf8_bom():
    base_dir = Path(__file__).parent.parent

    try:
        # Get all git-tracked files using -z to safely handle paths with spaces/newlines
        tracked_files_output = subprocess.check_output(
            ["git", "ls-files", "-z"], cwd=str(base_dir)
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return # Skip if not in a git repo or git is not installed

    offenders = []

    # Split by null byte
    tracked_files = [f.decode('utf-8') for f in tracked_files_output.split(b'\0') if f]

    for filepath in tracked_files:
        full_path = base_dir / filepath

        # Skip if file doesn't exist or is a directory
        if not full_path.is_file():
            continue

        if filepath in ALLOWLIST:
            continue

        try:
            with open(full_path, "rb") as f:
                header = f.read(3)
                # UTF-8 BOM is b'\xef\xbb\xbf'
                if header == b'\xef\xbb\xbf':
                    offenders.append(filepath)
        except IOError:
            pass # Skip unreadable files

    assert not offenders, (
        f"The following files contain a UTF-8 byte order mark (BOM):\n" +
        "\n".join(offenders) +
        "\nPlease remove the BOM from these files."
    )
