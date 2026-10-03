import pytest
from webchat import infer_location

def test_infer_location_no_match():
    assert infer_location("show me a map please") is None
    assert infer_location("") is None
    assert infer_location("for") is None
