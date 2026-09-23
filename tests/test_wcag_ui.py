import pytest
from html.parser import HTMLParser
import os

class A11yParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements_by_id = {}
        self.labels_for = []

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if 'id' in attr_dict:
            self.elements_by_id[attr_dict['id']] = {
                'tag': tag,
                'aria-label': attr_dict.get('aria-label')
            }
        if tag == 'label' and 'for' in attr_dict:
            self.labels_for.append(attr_dict['for'])

def test_index_html_wcag_labels():
    index_path = os.path.join(os.path.dirname(__file__), '..', 'index.html')
    with open(index_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    parser = A11yParser()
    parser.feed(html_content)

    elements_to_check = [
        'agent-prompt',
        'llm-api-key',
        'llm-model',
        'layer-select'
    ]

    for element_id in elements_to_check:
        assert element_id in parser.elements_by_id, f"Element with ID {element_id} not found."

        element = parser.elements_by_id[element_id]
        has_aria_label = bool(element['aria-label'])
        has_label_for = element_id in parser.labels_for

        assert has_aria_label or has_label_for, (
            f"Element '{element_id}' lacks a connected <label> or 'aria-label' attribute. "
            "This is a WCAG accessibility violation."
        )

def test_index_html_wcag_focus():
    index_path = os.path.join(os.path.dirname(__file__), '..', 'index.html')
    with open(index_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    assert ":focus-visible" in html_content, "Missing :focus-visible CSS rules for accessibility."

if __name__ == '__main__':
    pytest.main(['-v', __file__])
