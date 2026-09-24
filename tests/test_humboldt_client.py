import pytest
from unittest.mock import MagicMock, patch
import argparse
import sys

from humboldt import main

def test_humboldt_connection_error(mocker):
    # Mock inputs
    mocker.patch('builtins.input', side_effect=["test query", "exit"])

    # Mock print to verify output
    mock_print = mocker.patch('builtins.print')

    # Need to skip check_and_install_dependencies to speed up the test and avoid side-effects
    mocker.patch('humboldt.check_and_install_dependencies')

    # Mock argparse.ArgumentParser.parse_args
    args = argparse.Namespace(
        base_url="http://localhost:9999/v1/",
        api_key="sk-test",
        model="test",
        skip_deps=True,
        max_steps=1,
        debug=False
    )
    mocker.patch('argparse.ArgumentParser.parse_args', return_value=args)

    # Mock OpenAI client
    mock_openai_class = mocker.patch('humboldt.OpenAI', create=True)
    mock_client = mock_openai_class.return_value

    # Make the create call raise an Exception
    mock_client.chat.completions.create.side_effect = Exception("API connection error")

    # Run the function - it should not crash
    main()

    # Verify that an error message was printed
    printed_messages = [call[0][0] for call in mock_print.call_args_list if call[0]]
    assert any("Error connecting to LLM provider" in str(msg) for msg in printed_messages), f"Did not print connection error: {printed_messages}"
