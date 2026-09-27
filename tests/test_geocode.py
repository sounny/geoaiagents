import pytest
from unittest.mock import patch
from geocode import _SHARED_GEOCODE, get_coordinates, reverse_geocode_coordinates, geocode_locations

def test_shared_rate_limiter():
    """Verify that the shared rate limiters exist and have correct max_retries."""
    from geocode import _SHARED_GEOCODE, _SHARED_REVERSE
    assert _SHARED_GEOCODE.max_retries == 2
    assert _SHARED_REVERSE.max_retries == 2


@patch("geocode._SHARED_GEOCODE")
def test_get_coordinates_timeout_override(mock_geocode):
    """Verify get_coordinates passes timeout as a kwarg."""
    mock_geocode.return_value = None
    get_coordinates("Test City", timeout=5)

    mock_geocode.assert_called_once()
    kwargs = mock_geocode.call_args.kwargs
    assert kwargs.get("timeout") == 5


@patch("geocode._SHARED_REVERSE")
def test_reverse_geocode_timeout_override(mock_reverse):
    """Verify reverse_geocode_coordinates passes timeout as a kwarg."""
    mock_reverse.return_value = None
    reverse_geocode_coordinates("0,0", timeout=5)

    mock_reverse.assert_called_once()
    kwargs = mock_reverse.call_args.kwargs
    assert kwargs.get("timeout") == 5

@patch("geocode.OpenAI")
def test_main_api_connection_failure(mock_openai, capsys):
    """Verify geocode.py catches LLM API errors gracefully and runs fallback geocoding."""
    mock_client = mock_openai.return_value
    mock_client.chat.completions.create.side_effect = Exception("Mock LLM offline")

    import geocode
    import sys
    # We patch input to give it an address to geocode locally
    with patch("builtins.input", return_value="London"):
        # We need to stub _SHARED_GEOCODE to avoid actual network requests during the fallback
        with patch("geocode.get_coordinates", return_value=("London, UK", 51.5, -0.1)):
            with patch.object(sys, "argv", ["geocode.py"]):
                geocode.main()

    captured = capsys.readouterr()
    assert "[ERROR] API connection failed: Mock LLM offline" in captured.out
    # Assert fallback printed the table
    assert "| London | London, UK | 51.5 | -0.1 |" in captured.out
