import pytest
import webchat
from unittest.mock import patch, MagicMock

def test_webchat_provider_fallback_regression():
    with patch("webchat.OpenAI", create=True) as MockOpenAI:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        MockOpenAI.return_value = mock_client

        try:
            webchat.respond("where is Tokyo", [])
        except Exception as e:
            pytest.fail(f"webchat crashed on API error: {e}")
