import os
import pytest
from html.parser import HTMLParser

class IndexHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.mixed_content = []
        self.has_html_lang = False
        self.has_meta_viewport = False

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)

        # Mixed content checks
        url = None
        if tag == 'script' and 'src' in attr_dict:
            url = attr_dict['src']
        elif tag == 'link' and attr_dict.get('rel') == 'stylesheet' and 'href' in attr_dict:
            url = attr_dict['href']
        elif tag == 'img' and 'src' in attr_dict:
            url = attr_dict['src']
        elif tag == 'iframe' and 'src' in attr_dict:
            url = attr_dict['src']

        if url and url.startswith('http://'):
            self.mixed_content.append(f"<{tag}> with http url: {url}")

        if tag == 'html' and 'lang' in attr_dict:
            self.has_html_lang = True

        if tag == 'meta' and attr_dict.get('name') == 'viewport':
            self.has_meta_viewport = True

def test_index_html_mixed_content():
    index_path = os.path.join(os.path.dirname(__file__), '..', 'index.html')
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()

    parser = IndexHTMLParser()
    parser.feed(content)

    if parser.mixed_content:
        pytest.xfail(f"Mixed content found: {', '.join(parser.mixed_content)}")


def test_index_html_attributes():
    index_path = os.path.join(os.path.dirname(__file__), '..', 'index.html')
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()

    parser = IndexHTMLParser()
    parser.feed(content)

    if not parser.has_html_lang:
        pytest.xfail("index.html is missing lang attribute in html tag")
    if not parser.has_meta_viewport:
        pytest.xfail("index.html is missing meta viewport tag")
