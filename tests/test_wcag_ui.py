import pytest
from html.parser import HTMLParser

class AccessibleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.issues = []
        self.in_label = False

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)

        if tag == 'button':
            if 'aria-label' not in attr_dict and not self.in_label:
                self.issues.append(f"Button without aria-label: {attr_dict}")

        if tag == 'input':
            if 'aria-label' not in attr_dict and 'id' not in attr_dict:
                self.issues.append(f"Input without aria-label or id: {attr_dict}")

        if tag == 'label':
            self.in_label = True

    def handle_endtag(self, tag):
        if tag == 'label':
            self.in_label = False

def test_index_html_wcag():
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            html = f.read()
    except FileNotFoundError:
        pytest.skip("index.html not found, skipping UI test.")

    parser = AccessibleParser()
    parser.feed(html)

    assert not parser.issues, f"WCAG accessibility issues found: {parser.issues}"
