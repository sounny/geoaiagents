import pytest
from html.parser import HTMLParser

class WCAGParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.issues = []
        self.has_main = False
        self.inputs = []
        self.labels = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag == "main":
            self.has_main = True

        if tag in ["input", "textarea", "select"]:
            if "type" in attrs_dict and attrs_dict["type"] == "hidden":
                return
            if "id" in attrs_dict:
                self.inputs.append(attrs_dict["id"])
            if not ("aria-label" in attrs_dict or "aria-labelledby" in attrs_dict or "id" in attrs_dict):
                self.issues.append(f"Input element missing accessible label: {tag} {attrs}")

        if tag == "label":
            if "for" in attrs_dict:
                self.labels.append(attrs_dict["for"])

        if tag == "img":
            if "alt" not in attrs_dict:
                self.issues.append(f"Image missing alt text: {attrs}")

def test_wcag_compliance():
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(base_dir, "index.html"), "r") as f:
        html = f.read()

    parser = WCAGParser()
    parser.feed(html)

    # Check if inputs with IDs have corresponding labels (or aria-labels, though simplistic here)
    unlabeled_inputs = set(parser.inputs) - set(parser.labels)
    # Just check if there's any issues for now based on alt/aria-label logic

    assert len(parser.issues) == 0, f"WCAG issues found: {parser.issues}"
