import pytest
import geocode
from unittest.mock import patch, MagicMock

def test_geocode_provider_fallback_regression():
    with patch("geocode.OpenAI") as MockOpenAI:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Timeout")
        MockOpenAI.return_value = mock_client

        with patch("builtins.input", return_value="Test Location"):
            with patch("sys.argv", ["geocode.py"]):
                try:
                    geocode.main()
                except Exception as e:
                    pytest.fail(f"Geocode crashed on API error instead of handling gracefully: {e}")
