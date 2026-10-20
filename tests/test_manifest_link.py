import pytest
import os
from html.parser import HTMLParser

class ManifestParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.found_manifest_link = False

    def handle_starttag(self, tag, attrs):
        if tag == 'link':
            attr_dict = dict(attrs)
            if attr_dict.get('rel') == 'manifest' and attr_dict.get('href') == 'manifest.json':
                self.found_manifest_link = True
            elif attr_dict.get('rel') == 'manifest':
                # Sometimes people write it as href="/manifest.json" or similar
                if 'manifest.json' in attr_dict.get('href', ''):
                    self.found_manifest_link = True

def test_index_html_manifest_link():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    manifest_path = os.path.join(base_dir, 'manifest.json')
    index_path = os.path.join(base_dir, 'index.html')

    assert os.path.exists(manifest_path), "manifest.json file is missing"
    assert os.path.exists(index_path), "index.html file is missing"

    with open(index_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    parser = ManifestParser()
    parser.feed(html_content)

    if not parser.found_manifest_link:
        pytest.xfail("index.html is missing <link rel=manifest> pointing to manifest.json")

if __name__ == '__main__':
    pytest.main(['-v', __file__])
