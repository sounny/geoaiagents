import os
from html.parser import HTMLParser

class WCAGParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements = []
        self.labels_for = []
        self.current_tag = None

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag in ["input", "button", "select", "textarea"]:
            self.elements.append({"tag": tag, "attrs": attrs_dict, "text": ""})
            self.current_tag = self.elements[-1]
        elif tag == "label" and "for" in attrs_dict:
            self.labels_for.append(attrs_dict["for"])
        else:
            self.current_tag = None

    def handle_data(self, data):
        if self.current_tag is not None:
            self.current_tag["text"] += data.strip()

def test_index_html_wcag_compliance():
    file_path = os.path.join(os.path.dirname(__file__), '..', 'index.html')
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()

    parser = WCAGParser()
    parser.feed(html)

    violations = []
    for el in parser.elements:
        tag = el["tag"]
        attrs = el["attrs"]
        text = el["text"]

        has_aria = "aria-label" in attrs
        has_title = "title" in attrs
        has_id = "id" in attrs
        has_for_label = has_id and attrs["id"] in parser.labels_for
        has_text = bool(text)

        if tag in ["input", "select", "textarea"]:
            if not (has_aria or has_for_label or has_title):
                violations.append(f"<{tag} id={attrs.get('id', 'None')}> missing aria-label or associated <label>")
        elif tag == "button":
            if not (has_aria or has_title or has_text):
                violations.append(f"<button class={attrs.get('class', 'None')}> missing text, title, or aria-label")

    assert not violations, "WCAG Violations found:\n" + "\n".join(violations)
