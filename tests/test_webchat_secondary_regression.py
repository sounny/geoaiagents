import pytest
import webchat
from unittest.mock import patch, MagicMock

def test_webchat_provider_secondary_fallback_regression():
    with patch("webchat.OpenAI", create=True) as MockOpenAI:
        mock_client = MagicMock()

        # First call succeeds, returns a function call
        mock_message1 = MagicMock()
        mock_message1.function_call.name = "geocode_locations"
        mock_message1.function_call.arguments = '{"locations": "Tokyo"}'
        mock_choice1 = MagicMock()
        mock_choice1.message = mock_message1
        mock_response1 = MagicMock()
        mock_response1.choices = [mock_choice1]

        # Second call throws exception
        mock_client.chat.completions.create.side_effect = [mock_response1, Exception("API Error 2")]
        MockOpenAI.return_value = mock_client

        with patch("webchat.run_tool", return_value=("geocode_locations", "table")):
            with patch("webchat.extract_map_coords", return_value=[(35, 139)]):
                try:
                    # Should not crash
                    reply, map_html, logs, table = webchat.respond("where is Tokyo", [])
                    assert "Error communicating with AI provider" in reply
                except Exception as e:
                    pytest.fail(f"webchat crashed on secondary API error: {e}")
