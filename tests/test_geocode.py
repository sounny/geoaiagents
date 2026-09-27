import pytest
from unittest.mock import MagicMock, patch
import geocode

def test_geocode_limiter_setup():
    assert geocode.geocode_limiter.max_retries == 2
    assert geocode.reverse_limiter.max_retries == 2
    assert geocode.geocode_limiter.min_delay_seconds == 1
    assert geocode.reverse_limiter.min_delay_seconds == 1

@patch('geocode.geocode_limiter')
def test_get_coordinates_passes_timeout(mock_geocode_limiter):
    mock_location = MagicMock()
    mock_location.address = "Test Address"
    mock_location.latitude = 12.34
    mock_location.longitude = 56.78
    mock_geocode_limiter.return_value = mock_location

    addr, lat, lon = geocode.get_coordinates("Test query", timeout=5, language="fr")

    assert addr == "Test Address"
    assert lat == 12.34
    assert lon == 56.78
    mock_geocode_limiter.assert_called_once_with(
        "Test query",
        language="fr",
        viewbox=None,
        bounded=False,
        timeout=5
    )

@patch('geocode.reverse_limiter')
def test_reverse_geocode_coordinates_passes_timeout(mock_reverse_limiter):
    mock_location = MagicMock()
    mock_location.address = "Reverse Test Address"
    mock_reverse_limiter.return_value = mock_location

    result = geocode.reverse_geocode_coordinates("12.34, 56.78", timeout=4, language="es")

    assert "Reverse Test Address" in result
    mock_reverse_limiter.assert_called_once_with((12.34, 56.78), language="es", timeout=4)

@patch('geocode.OpenAI')
@patch('sys.argv', ['geocode.py'])
@patch('builtins.input', return_value='Test Input')
def test_main_fallback_output(mock_input, mock_openai, capsys):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.function_call = None
    mock_client.chat.completions.create.return_value = mock_response

    with patch('geocode.geocode_locations', return_value="| Input | Matched Address |\n|---|---|") as mock_geocode_locs:
        geocode.main()

    mock_geocode_locs.assert_called_once_with("Test Input")
    captured = capsys.readouterr()
    assert "Datum: WGS84" in captured.out
    assert "| Input | Matched Address |" in captured.out
