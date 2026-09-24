import pytest
from html.parser import HTMLParser

class WCAGParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inputs = []
        self.buttons = []
        self.labels_for = []

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag == "input":
            self.inputs.append(attr_dict)
        elif tag == "button":
            self.buttons.append(attr_dict)
        elif tag == "label":
            if "for" in attr_dict:
                self.labels_for.append(attr_dict["for"])

def test_wcag_accessibility():
    parser = WCAGParser()
    with open("index.html", "r", encoding="utf-8") as f:
        parser.feed(f.read())

    for inp in parser.inputs:
        input_type = inp.get("type", "text")
        if input_type not in ["hidden"]:
            has_aria = "aria-label" in inp or "aria-labelledby" in inp
            has_label = "id" in inp and inp["id"] in parser.labels_for
            assert has_aria or has_label, f"Input element missing accessibility label: {inp}"
