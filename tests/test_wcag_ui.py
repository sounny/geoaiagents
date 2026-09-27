import pytest
from bs4 import BeautifulSoup
import os

def test_wcag_compliance():
    """Test index.html for basic WCAG compliance (aria-labels, label tags)"""
    html_path = os.path.join(os.path.dirname(__file__), '..', 'index.html')
    if not os.path.exists(html_path):
        pytest.skip("index.html not found")

    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # Check buttons
    buttons = soup.find_all('button')
    for btn in buttons:
        # A button must have text content or an aria-label
        has_text = bool(btn.get_text(strip=True))
        has_aria_label = btn.has_attr('aria-label')
        has_title = btn.has_attr('title')
        assert has_text or has_aria_label or has_title, f"Button lacks accessible name: {btn}"

    # Check inputs
    inputs = soup.find_all('input')
    for inp in inputs:
        # Check if type is hidden
        if inp.get('type') == 'hidden':
            continue

        has_aria_label = inp.has_attr('aria-label')
        has_id = inp.has_attr('id')

        # If it has an id, check if there's a corresponding label
        has_label = False
        if has_id:
            label = soup.find('label', {'for': inp['id']})
            has_label = label is not None

        assert has_aria_label or has_label, f"Input lacks accessible name: {inp}"
