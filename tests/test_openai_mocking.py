import pytest
import sys
import geocode

def test_geocode_main_mocking(mocker, capsys):
    mock_openai = mocker.patch("geocode.OpenAI")
    mocker.patch.object(sys, 'argv', ['geocode.py'])
    mocker.patch('builtins.input', return_value="Paris, France")

    mock_client = mock_openai.return_value
    mock_client.chat.completions.create.return_value.choices = [
        mocker.MagicMock(message=mocker.MagicMock(
            function_call=None,
            content="Mocked response"
        ))
    ]

    geocode.main()

    captured = capsys.readouterr()
    assert "Datum: WGS84" in captured.out
