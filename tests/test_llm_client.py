import pytest
from unittest.mock import MagicMock, patch
import openai
from openai import APIConnectionError, APIError
import json
import argparse
from io import StringIO
import sys

from geoai_cli import _run_chat_mode

def test_cli_chat_mode_connection_error(mocker):
    # Mock inputs
    mocker.patch('builtins.input', side_effect=["test query", "exit"])

    # Mock print to verify output
    mock_print = mocker.patch('builtins.print')

    # Mock OpenAI client
    # The client is created inside _run_chat_mode: client = OpenAI(...)
    # Because of how we patch, we should mock 'openai.OpenAI' since it's imported locally
    mock_openai_class = mocker.patch('geoai_cli.OpenAI', create=True)
    mock_client = mock_openai_class.return_value

    # Make the create call raise an APIConnectionError
    mock_client.chat.completions.create.side_effect = APIConnectionError(request=MagicMock())

    args = argparse.Namespace(
        base_url="http://localhost:9999/v1/",
        api_key="sk-test",
        model="test",
        max_steps=1,
        debug=False
    )
    registry = MagicMock()

    # Run the function - it should not crash
    _run_chat_mode(args, registry)

    # Verify that an error message was printed
    printed_messages = [call[0][0] for call in mock_print.call_args_list if call[0]]
    assert any("Error connecting to LLM provider" in str(msg) for msg in printed_messages), f"Did not print connection error: {printed_messages}"
