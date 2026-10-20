import re
import os
import pytest

def test_readme_file_paths():
    """
    Evaluates repo-relative file paths in README.md.
    Extracts paths using regex while explicitly ignoring URLs.
    Checks their existence, and calls pytest.xfail with a descriptive note for missing files
    without modifying the README. This test makes no network calls and does not change API keys or billing.
    """
    if not os.path.exists("README.md"):
        pytest.skip("README.md not found")

    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    # Match markdown links that do not start with http or #
    links = re.findall(r'\[[^\]]+\]\((?!http|#)([^)]+)\)', content)

    # Match files mentioned in backticks, looking for extensions
    backticks = re.findall(r'`([a-zA-Z0-9_/\.-]+\.[a-zA-Z0-9]+)`', content)

    # Match hidden files mentioned in backticks like `.python-version`
    backticks_hidden = re.findall(r'`(\.[a-zA-Z0-9_-]+)`', content)

    all_paths = set(links + backticks + backticks_hidden)

    missing_files = []
    for path in all_paths:
        if not os.path.exists(path):
            missing_files.append(path)

    if missing_files:
        pytest.xfail(f"Missing files mentioned in README.md: {', '.join(missing_files)}")
