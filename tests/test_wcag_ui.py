import os
import re

def test_index_html_wcag_compliance():
    """Verify that all inputs, selects, and textareas have basic accessibility tags."""
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Check inputs
    inputs = re.findall(r'<input[^>]+>', content)
    for inp in inputs:
        if 'type="hidden"' in inp:
            continue
        has_aria_label = 'aria-label=' in inp
        has_label_tag = False  # For a full check we'd parse <label for="...">, but let's stick to aria-label for our patched fields
        assert has_aria_label or 'type="submit"' in inp or 'type="button"' in inp, f"Input element is missing aria-label: {inp}"

    # Check textareas
    textareas = re.findall(r'<textarea[^>]+>', content)
    for ta in textareas:
        has_aria_label = 'aria-label=' in ta
        assert has_aria_label, f"Textarea is missing aria-label: {ta}"

    # Check selects
    selects = re.findall(r'<select[^>]+>', content)
    for sel in selects:
        has_aria_label = 'aria-label=' in sel
        assert has_aria_label, f"Select is missing aria-label: {sel}"
