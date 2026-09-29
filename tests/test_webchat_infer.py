import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from webchat import infer_location

def test_infer_location_empty():
    assert infer_location("") is None

def test_infer_location_whitespace():
    assert infer_location("   ") is None
    assert infer_location("\t\n") is None

def test_infer_location_extracted_whitespace():
    assert infer_location("for   ") is None

def test_infer_location_valid():
    assert infer_location("for London") == "London"
    assert infer_location("map for New York, NY") == "New York, NY"
