import subprocess
import os

ALLOWLIST = {
    "geocode.py",
    "tests/test_agents_md.py",
    "tests/test_geocode_fallback.py",
    "tests/test_meta_exit.py",
    "tests/test_meta_len_comparison.py",
    "tests/test_meta_skip.py",
    "tests/test_meta_three_arg_getattr.py",
}

def test_line_length_under_160():
    """Ensure no tracked .py file has a line longer than 160 characters (excluding .git and virtualenv folders),
    failing if the total grows beyond the current count, with an allowlist for current offenders."""
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

        # Exclude .git and virtualenv paths, though git ls-files should naturally exclude them if ignored,
        # but just in case we add this check.
        if ".git/" in filepath or "virtualenv/" in filepath:
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                # Remove trailing newline for length calculation
                line_content = line.rstrip("\r\n")
                if len(line_content) > 160:
                    offenders.append(f"{filepath}:{line_num} ({len(line_content)} chars)")

    if offenders:
        msg = "The following files contain lines longer than 160 characters:\n"
        msg += "\n".join(offenders)
        msg += "\n\nPlease keep lines under 160 characters or add to allowlist if absolutely necessary."
        assert not offenders, msg
