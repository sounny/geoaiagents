import sys
import os

# Add to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import webchat
from unittest.mock import MagicMock
import urllib.request
import urllib.error
import subprocess
import threading
import time

def test_respond_missing_message(mocker):
    # Mock LLM response
    mock_response = MagicMock()

    mock_msg = MagicMock()
    mock_msg.content = "I didn't get that."
    mock_msg.function_call = None
    mock_response.choices = [MagicMock(message=mock_msg)]

    mocker.patch("webchat.call_llm_with_retry", return_value=mock_response)

    # Ensure no exception is raised and return is as expected
    reply, map_html, logs, table = webchat.respond(None, [])

    assert reply == "I didn't get that."

def test_head_returns_405():
    from fastapi.testclient import TestClient

    app = webchat.create_app()
    client = TestClient(app)

    # Try a HEAD request
    response = client.head("/")
    assert response.status_code == 405

    response = client.options("/")
    assert response.status_code == 405
    assert response.text == "Method Not Allowed"

    # Standard GET should be 200
    response = client.get("/")
    assert response.status_code == 200
