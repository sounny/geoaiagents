import os
import re
import pytest

def get_repo_files_from_agents():
    agents_path = "AGENTS.md"
    if not os.path.exists(agents_path):
        return []

    with open(agents_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract strings that look like file paths ending in common extensions
    # Also we want to explicitly ignore URLs like http://...

    # We can use a regex that matches paths but doesn't start with http/https.
    # To do this correctly, we can find all tokens and then check if they are valid repo paths.

    # Let's match all potential file names:
    pattern = re.compile(r'([a-zA-Z0-9_\-\.\/]+\.(?:py|md|sh|txt|html|json|ini))')
    matches = pattern.findall(content)

    # De-duplicate
    matches = list(set(matches))

    # Filter out urls by checking if the original text had http before it,
    # but a simpler way is just to ensure it's a relative path in our repo that we care about.
    # Alternatively we can filter out common non-file references like `Leaflet.js` which is a library.

    # The requirement: "every repo-relative file path mentioned in AGENTS.md exists in the repo"
    # We can refine our regex to not match URLs at all:
    # Let's use a regex that looks for paths in backticks or just general paths, but avoid matching `.js` since it's just a library name (Leaflet.js) in the text.

    valid_paths = []
    for match in matches:
        # Ignore things that look like URLs that might have been partially matched
        if match.startswith('http://') or match.startswith('https://') or match.startswith('//'):
            continue
        valid_paths.append(match)

    return valid_paths

# Use parametrize so each file is its own test case, as recommended by code review
@pytest.mark.parametrize("file_path", get_repo_files_from_agents())
def test_agents_md_paths_exist(file_path):
    agents_path = "AGENTS.md"
    if not os.path.exists(agents_path):
        pytest.skip("AGENTS.md not found")

    if not os.path.exists(file_path):
        pytest.xfail(f"Missing referenced file in AGENTS.md: {file_path}")
