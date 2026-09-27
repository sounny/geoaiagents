import pytest
from html.parser import HTMLParser

class AccessibleFormParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inputs = []
        self.labels = []

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag == "input" or tag == "textarea" or tag == "button":
            # Just capture the tag info
            self.inputs.append((tag, attr_dict))
        elif tag == "label":
            if "for" in attr_dict:
                self.labels.append(attr_dict["for"])

def test_index_accessibility():
    with open("index.html", "r") as f:
        html = f.read()

    parser = AccessibleFormParser()
    parser.feed(html)

    # Check if inputs either have a corresponding label or an aria-label
    for tag, attrs in parser.inputs:
        if tag == "button" and "aria-label" not in attrs and "id" not in attrs:
            # this is a bit relaxed for now
            continue

        has_aria = "aria-label" in attrs
        has_label = attrs.get("id") in parser.labels

        # We need AT LEAST ONE
        # if neither, fail unless type="hidden"
        if attrs.get("type") == "hidden":
            continue

        assert has_aria or has_label, f"{tag} with attrs {attrs} missing accessibility label"
