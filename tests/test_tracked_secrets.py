import os
import re
import subprocess
import pytest

# Patterns for common secrets
SECRET_PATTERNS = {
    "AWS Access Key": re.compile(r'\bAKIA[0-9A-Z]{16}\b'),
    "Private Key Header": re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----'),
    "Generic API Key": re.compile(r'(?i)api_key\s*=\s*[\'"]([^\'"]{20,})[\'"]')
}

# Allowlist mapping filepath to a list of allowed matches.
ALLOWLIST = {}

def get_tracked_text_files():
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True,
            text=True,
            check=True
        )
        files = result.stdout.splitlines()
        # Filter for files that exist and can be opened as text
        for f in files:
            if not os.path.isfile(f):
                continue
            # Try opening the file to check if it's text
            try:
                with open(f, 'r', encoding='utf-8') as file_handle:
                    file_handle.read()
                yield f
            except UnicodeDecodeError:
                continue
    except subprocess.CalledProcessError:
        pytest.skip("Not a git repository or git is not installed")


def test_tracked_files_no_secrets():
    offenders = []

    for filepath in get_tracked_text_files():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            pytest.fail(f"Could not read {filepath}: {e}")

        allowed_in_file = ALLOWLIST.get(filepath, [])

        for line_num, line in enumerate(content.splitlines(), start=1):
            for secret_type, pattern in SECRET_PATTERNS.items():
                for match in pattern.finditer(line):
                    # For Generic API Key, we want to match the whole literal or the captured group
                    matched_str = match.group(0)
                    if matched_str not in allowed_in_file:
                        offenders.append(f"{filepath}:{line_num}: Found {secret_type}: {matched_str}")

    if offenders:
        pytest.fail("Found potential secrets in tracked text files:\n" + "\n".join(offenders))
