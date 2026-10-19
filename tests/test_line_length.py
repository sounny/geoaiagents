import subprocess
import os

ALLOWLIST = {
    "geocode.py",
    "tests/test_file_loaders.py",
    "tests/test_webchat_tables.py",
}

def test_line_length_under_120():
    """Ensure no tracked .py file has a line longer than 120 characters, with an allowlist."""
    try:
        # Get all tracked files
        tracked_files = subprocess.check_output(
            ["git", "ls-files"], text=True
        ).splitlines()
    except subprocess.CalledProcessError:
        return

    py_files = [f for f in tracked_files if f.endswith(".py")]

    offenders = []

    for filepath in py_files:
        if filepath in ALLOWLIST:
            continue

        if not os.path.exists(filepath):
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                # Remove trailing newline for length calculation
                line_content = line.rstrip("\r\n")
                if len(line_content) > 120:
                    offenders.append(f"{filepath}:{line_num} ({len(line_content)} chars)")

    if offenders:
        msg = "The following files contain lines longer than 120 characters:\n"
        msg += "\n".join(offenders)
        msg += "\n\nPlease keep lines under 120 characters."
        assert not offenders, msg
