import os
import pytest
from html.parser import HTMLParser

class IndexHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lang = None
        self.in_title = False
        self.title_text = ""
        self.local_links = []

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag == "html":
            self.lang = attr_dict.get("lang")
        elif tag == "title":
            self.in_title = True

        # Check href and src for local links
        for attr_name in ["href", "src"]:
            if attr_name in attr_dict:
                link = attr_dict[attr_name]
                # Ignore empty links, absolute URLs, data URIs, and anchors
                if (link and
                    not link.startswith("http://") and
                    not link.startswith("https://") and
                    not link.startswith("data:") and
                    not link.startswith("#")):
                    self.local_links.append(link)

    def handle_data(self, data):
        if self.in_title:
            self.title_text += data

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

def test_index_html_structure_and_links():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    index_path = os.path.join(repo_root, "index.html")

    with open(index_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    parser = IndexHTMLParser()
    parser.feed(html_content)

    # 1. Check lang attribute
    assert parser.lang is not None, "<html> tag is missing 'lang' attribute"
    assert parser.lang.strip() != "", "<html> 'lang' attribute is empty"

    # 2. Check non-empty title
    assert parser.title_text.strip() != "", "<title> tag is empty or missing"

    # 3. Check local src/href links point to existing files
    for link in parser.local_links:
        file_path = os.path.join(repo_root, link)
        assert os.path.exists(file_path), f"Local link '{link}' points to a non-existent file."

if __name__ == "__main__":
    pytest.main(["-v", __file__])
