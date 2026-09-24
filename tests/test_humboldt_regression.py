import pytest
import humboldt
from unittest.mock import patch, MagicMock

def test_humboldt_provider_fallback_regression():
    with patch("humboldt.OpenAI", create=True) as MockOpenAI:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        MockOpenAI.return_value = mock_client

        with patch("builtins.input", side_effect=["where is Berlin", "exit"]):
            with patch("sys.argv", ["humboldt.py", "--skip-deps"]):
                try:
                    humboldt.main()
                except Exception as e:
                    pytest.fail(f"Humboldt crashed on API error instead of handling gracefully: {e}")
