import pytest
from unittest.mock import MagicMock
import sys
import geocode

def test_geocode_fallback_on_provider_error(mocker, capsys):
    """Test that when the LLM provider fails, geocode.py gracefully falls back to local geocoding."""
    mocker.patch("builtins.input", return_value="Paris")
    mocker.patch("sys.argv", ["geocode.py"])

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("Simulated connection error")
    mocker.patch("geocode.OpenAI", return_value=mock_client)

    mock_geocode = mocker.patch("geocode.geocode_locations", return_value="| Input | Matched Address | Latitude | Longitude |\n|-------|-----------------|----------|-----------|\n| Paris | Paris, France | 48.85 | 2.35 |")

    geocode.main()

    captured = capsys.readouterr()
    assert "Error communicating with provider:" in captured.out
    assert "Falling back to local geocoding..." in captured.out
    assert "Paris, France" in captured.out
    assert mock_geocode.call_count == 1
