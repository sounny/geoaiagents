import pytest
from unittest.mock import MagicMock, patch
import sys
# Mock gradio so we don't have to install it
sys.modules['gradio'] = MagicMock()

from webchat import respond

def test_webchat_connection_error(mocker):
    # Mock OpenAI client
    mock_openai_class = mocker.patch('webchat.client')

    # Make the create call raise an Exception
    mock_openai_class.chat.completions.create.side_effect = Exception("API connection error")

    # Run the function - it should not crash
    reply, map_html, logs, table = respond("test query", [])

    # Verify that an error message was returned
    assert "Error connecting to LLM provider" in reply
