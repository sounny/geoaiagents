import pytest
import geoai_cli
from unittest.mock import patch, MagicMock

def test_geoai_cli_provider_fallback_regression():
    with patch("geoai_cli.OpenAI", create=True) as MockOpenAI:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        MockOpenAI.return_value = mock_client

        with patch("builtins.input", side_effect=["where is Paris", "exit"]):
            with patch("sys.argv", ["geoai_cli.py", "chat"]):
                try:
                    geoai_cli.main()
                except Exception as e:
                    pytest.fail(f"GeoAI CLI crashed on API error: {e}")
