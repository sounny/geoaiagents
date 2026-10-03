import sys
import os
import pytest

# Ensure the root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import webchat

def test_create_map_html_empty():
    """Test that create_map_html returns an empty string when given an empty list."""
    assert webchat.create_map_html([]) == ""
