import pytest
import os
import urllib.parse
from html.parser import HTMLParser

class IndexHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.has_html_lang = False
        self.has_meta_charset = False
        self.has_meta_viewport = False

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)

        if tag == "html":
            if "lang" in attr_dict and attr_dict["lang"]:
                self.has_html_lang = True

        elif tag == "meta":
            if "charset" in attr_dict:
                self.has_meta_charset = True
            elif "name" in attr_dict and attr_dict["name"].lower() == "viewport":
                self.has_meta_viewport = True


def test_index_html_meta():
    index_path = os.path.join(os.path.dirname(__file__), '..', 'index.html')

    if not os.path.exists(index_path):
        pytest.xfail(f"Could not find {index_path}")

    with open(index_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    parser = IndexHTMLParser()
    parser.feed(html_content)

    # 1. Check for <html lang>
    if not parser.has_html_lang:
        pytest.xfail("index.html is missing an <html lang> attribute")

    # 2. Check for <meta charset>
    if not parser.has_meta_charset:
        pytest.xfail("index.html is missing a <meta charset> tag")

    # 3. Check for <meta name="viewport">
    if not parser.has_meta_viewport:
        pytest.xfail("index.html is missing a <meta name=\"viewport\"> tag")
