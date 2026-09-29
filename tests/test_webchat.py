import pytest
from webchat import infer_location

def test_infer_location_paris():
    assert infer_location('Please show a map for Paris, France') == 'Paris, France'

def test_infer_location_empty():
    assert infer_location('') is None

def test_infer_location_whitespace():
    # As per current implementation, a whitespace-only location matches the regex.
    # But issue states "Do not redo empty/whitespace-only infer_location PRs".
    # The current implementation in webchat.py (untouched by this PR):
    # m = re.search(r"for ([A-Za-z0-9, ]+)", message, re.IGNORECASE)
    # if m: return m.group(1).strip()
    # It returns empty string if matched group only contains spaces because of `.strip()`.
    # Let's test this current behavior without changing infer_location.
    assert infer_location('Please show a map for   ') == ''

def test_infer_location_no_match():
    assert infer_location('What is the weather today?') is None
