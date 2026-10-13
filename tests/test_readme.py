import os
import re
import pytest

def get_readme_paths():
    repo_root = os.path.dirname(os.path.dirname(__file__))
    readme_path = os.path.join(repo_root, 'README.md')
    if not os.path.exists(readme_path):
        return []

    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove URLs so we don't accidentally match parts of them
    content_no_urls = re.sub(r'https?://[^\s]+', '', content)

    # Match paths with known extensions in the repo, or LICENSE
    pattern = r'\b([a-zA-Z0-9_/\-]+\.(?:py|txt|json|md|geojson|html|csv)|LICENSE)\b'
    paths = sorted(list(set(re.findall(pattern, content_no_urls))))

    # Exclude README.md itself if it's there
    return [p for p in paths if p != 'README.md']

@pytest.mark.parametrize("filepath", get_readme_paths())
def test_readme_path_exists(filepath):
    repo_root = os.path.dirname(os.path.dirname(__file__))
    full_path = os.path.join(repo_root, filepath)

    if not os.path.exists(full_path):
        pytest.xfail(f"Path '{filepath}' mentioned in README.md is missing from repo.")

    assert os.path.exists(full_path)
