import os
import re
import subprocess

def test_md_relative_links():
    """
    Parses every tracked .md file and fails on relative links whose target file does not exist
    (ignores http/https/mailto links and anchors).
    """
    out = subprocess.check_output(["git", "ls-files", "*.md"]).decode("utf-8")
    files = [f for f in out.splitlines() if f.strip()]

    # Allowlist for existing offenders (if any found)
    allowlist = set()

    broken_links = []

    for f in files:
        if not os.path.exists(f):
            continue
        with open(f, "r", encoding="utf-8") as file_obj:
            content = file_obj.read()

        # Match markdown links [text](target), being careful to exclude titles
        links = re.findall(r'\[[^\]]*\]\(([^)]+)\)', content)
        for link in links:
            # Handle titles like: `[text](file.md "Title")`
            # Target is the first part separated by spaces if title exists
            raw_target = link.split()[0].strip()

            if raw_target.startswith(("http://", "https://", "mailto:", "#")):
                continue

            target_path = raw_target.split('#')[0].strip()
            if not target_path:
                continue

            dir_name = os.path.dirname(f)
            full_target_path = os.path.normpath(os.path.join(dir_name, target_path))

            if not os.path.exists(full_target_path):
                link_key = f"{f}:{link}"
                if link_key not in allowlist:
                    broken_links.append((f, link, full_target_path))

    assert not broken_links, f"Found broken relative links in markdown files: {broken_links}"
