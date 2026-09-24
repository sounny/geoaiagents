import os
import pytest
from bs4 import BeautifulSoup

def test_wcag_compliance():
    index_path = os.path.join(os.path.dirname(__file__), '..', 'index.html')
    with open(index_path, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    # Check buttons have aria-label or text
    buttons = soup.find_all('button')
    for button in buttons:
        has_text = bool(button.text.strip())
        has_aria = button.has_attr('aria-label')
        has_title = button.has_attr('title')
        assert has_text or has_aria or has_title, f"Button {button} missing accessible name"

    # Check inputs have labels
    inputs = soup.find_all('input')
    for inp in inputs:
        inp_id = inp.get('id')
        if inp_id:
            label = soup.find('label', {'for': inp_id})
            has_aria = inp.has_attr('aria-label')
            assert label or has_aria, f"Input {inp} missing label or aria-label"

    # Check images have alt text
    images = soup.find_all('img')
    for img in images:
        assert img.has_attr('alt'), f"Image {img} missing alt text"
