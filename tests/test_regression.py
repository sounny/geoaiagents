import sys
import json
import pytest
from unittest.mock import MagicMock, patch

import geocode

def test_geocode_main_function_calling_flow(capsys):
    # Mock inputs and args
    test_args = ["geocode.py", "--base-url", "http://test", "--api-key", "test-key"]
    test_input = "Austin, TX; Paris, France"

    # Mock responses
    class MockMessage:
        def __init__(self, content, function_call=None, name=None):
            self.content = content
            self.function_call = function_call
            self.name = name

    class MockFunctionCall:
        def __init__(self, name, arguments):
            self.name = name
            self.arguments = arguments

    class MockChoice:
        def __init__(self, message):
            self.message = message

    class MockResponse:
        def __init__(self, choices):
            self.choices = choices

    mock_func_call = MockFunctionCall(
        name="geocode_locations",
        arguments=json.dumps({"locations": "Austin, TX; Paris, France"})
    )
    first_response = MockResponse([MockChoice(MockMessage(content=None, function_call=mock_func_call))])
    second_response = MockResponse([MockChoice(MockMessage(content="Here is the table."))])

    mock_client_instance = MagicMock()
    mock_client_instance.chat.completions.create.side_effect = [first_response, second_response]

    with patch("geocode.OpenAI", return_value=mock_client_instance), \
         patch.object(sys, "argv", test_args), \
         patch("builtins.input", return_value=test_input), \
         patch("geocode.get_coordinates", side_effect=[
             ("Austin, Texas, United States", 30.2711286, -97.7436995),
             ("Paris, Île-de-France, France", 48.8588897, 2.3200410217200766)
         ]):

        geocode.main()

    captured = capsys.readouterr()

    # Assertions
    assert "Here is the table." in captured.out
    assert "Datum: WGS84" in captured.out
    assert mock_client_instance.chat.completions.create.call_count == 2
