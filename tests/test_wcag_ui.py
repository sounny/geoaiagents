import pytest
from bs4 import BeautifulSoup

def test_index_html_has_aria_labels():
    with open('index.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    buttons = soup.find_all('button')
    inputs = soup.find_all('input')
    selects = soup.find_all('select')

    # Check that interactive elements have aria-labels or associated labels
    # This is a very basic check
    for button in buttons:
        # A button might have text instead of aria-label
        assert button.get('aria-label') or button.text.strip(), f"Button missing text or aria-label: {button}"

    for input_el in inputs:
        # Hidden inputs don't need aria labels
        if input_el.get('type') != 'hidden':
             assert input_el.get('aria-label') or input_el.get('id'), f"Input missing aria-label or id: {input_el}"
