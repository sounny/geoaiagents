import pytest
from unittest.mock import patch, MagicMock
import sys
import geocode
from geopy.exc import GeocoderTimedOut

def test_global_rate_limiter_configured():
    assert geocode.geocode_rate_limited.max_retries == 2
    assert geocode.reverse_rate_limited.max_retries == 2
    assert geocode.geocode_rate_limited.min_delay_seconds == 1
    assert geocode.reverse_rate_limited.min_delay_seconds == 1

@patch("geocode.geocode_rate_limited")
def test_get_coordinates_passes_timeout(mock_rate_limited):
    mock_rate_limited.return_value = MagicMock(address="Test Address", latitude=10.0, longitude=20.0)
    geocode.get_coordinates("Test query", timeout=5)
    mock_rate_limited.assert_called_once_with(
        "Test query",
        language="en",
        viewbox=None,
        bounded=False,
        timeout=5,
    )

@patch("geocode.reverse_rate_limited")
def test_reverse_geocode_coordinates_passes_timeout(mock_rate_limited):
    mock_rate_limited.return_value = MagicMock(address="Test Address")
    geocode.reverse_geocode_coordinates("10.0, 20.0", timeout=5)
    mock_rate_limited.assert_called_once_with((10.0, 20.0), language="en", timeout=5)

@patch("geocode.OpenAI")
@patch("sys.argv", ["geocode.py"])
def test_main_openai_mocking(mock_openai, capsys):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client

    mock_message = MagicMock()
    mock_message.function_call = None
    mock_message.content = "Mocked LLM Response"
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=mock_message)]
    mock_client.chat.completions.create.return_value = mock_response

    with patch("builtins.input", return_value="Test Location"):
        geocode.main()

    captured = capsys.readouterr()
    assert "Datum: WGS84" in captured.out

@patch("geocode.OpenAI")
@patch("sys.argv", ["geocode.py"])
def test_main_openai_exception(mock_openai, capsys):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_client.chat.completions.create.side_effect = Exception("API Timeout")

    with patch("builtins.input", return_value="Test Location"):
        geocode.main()

    captured = capsys.readouterr()
    assert "LLM API error: API Timeout" in captured.out
    assert "Datum: WGS84" in captured.out
