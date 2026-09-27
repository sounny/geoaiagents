import pytest
from unittest.mock import patch, MagicMock
import sys
import geocode
import builtins
import time

# Mock OpenAI client response to avoid actual API calls during testing
class MockMessage:
    def __init__(self, content, function_call=None):
        self.content = content
        self.function_call = function_call

class MockChoice:
    def __init__(self, message):
        self.message = message

class MockCompletion:
    def __init__(self, choices):
        self.choices = choices

class MockCompletions:
    def create(self, **kwargs):
        # Check if function call is allowed
        if kwargs.get('function_call') == 'auto':
            # Mock the first response where LLM decides to call the function
            mock_function_call = MagicMock()
            mock_function_call.name = "geocode_locations"
            mock_function_call.arguments = '{"locations": "Paris, France"}'
            return MockCompletion([MockChoice(MockMessage(content=None, function_call=mock_function_call))])
        else:
            # Mock the second response where LLM formats the final output
            return MockCompletion([MockChoice(MockMessage(content="Here is the formatted table."))])

class MockChat:
    def __init__(self):
        self.completions = MockCompletions()

class MockOpenAIClient:
    def __init__(self, **kwargs):
        self.chat = MockChat()

@pytest.fixture
def mock_openai_client():
    with patch('geocode.OpenAI', side_effect=MockOpenAIClient) as mock:
        yield mock

@pytest.fixture
def mock_sys_argv():
    with patch('sys.argv', ['geocode.py']):
        yield

@pytest.fixture
def mock_time_sleep():
    with patch('time.sleep', return_value=None):
        yield

@pytest.fixture
def mock_input():
    with patch.object(builtins, 'input', return_value="Paris, France"):
        yield

@pytest.fixture
def mock_geopy():
    with patch('geocode.shared_geocode') as mock_geocode:
        mock_location = MagicMock()
        mock_location.address = "Paris, Ile-de-France, France"
        mock_location.latitude = 48.8566
        mock_location.longitude = 2.3522
        mock_geocode.return_value = mock_location
        yield mock_geocode

def test_geocode_main_cli_deterministic(mock_openai_client, mock_sys_argv, mock_time_sleep, mock_input, mock_geopy, capsys):
    # Run the main function
    geocode.main()

    # Capture the output
    captured = capsys.readouterr()

    # Assert expected output is present
    assert "Here is the formatted table." in captured.out
    assert "Datum: WGS84 (coordinates shown in Decimal Degrees)." in captured.out
