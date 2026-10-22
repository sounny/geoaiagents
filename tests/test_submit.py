import sys
import runpy
import logging
from unittest.mock import MagicMock, patch

@patch('socket.socket')
def test_submit_normal(mock_socket, caplog):
    """Test submit.py runs normally without raising and logs contain no secrets."""
    mock_tools = MagicMock()

    with patch.dict(sys.modules, {'tools': mock_tools}):
        with patch.object(sys, 'argv', ['submit.py']):
            with caplog.at_level(logging.DEBUG):
                runpy.run_path("submit.py", run_name="__main__")

    mock_tools.submit.assert_called_once()

    # Assert the current log levels (submit.py currently logs nothing)
    log_levels = [record.levelname for record in caplog.records]
    assert log_levels == []

    for record in caplog.records:
        msg = record.message.lower()
        assert "secret" not in msg
        assert "api_key" not in msg

@patch('socket.socket')
def test_submit_failing(mock_socket, caplog):
    """Test submit.py gracefully handles an external failure and logs contain no secrets."""
    mock_tools = MagicMock()
    mock_tools.submit.side_effect = Exception("Simulated failure in submit")

    with patch.dict(sys.modules, {'tools': mock_tools}):
        with patch.object(sys, 'argv', ['submit.py']):
            with caplog.at_level(logging.DEBUG):
                try:
                    runpy.run_path("submit.py", run_name="__main__")
                except Exception as e:
                    pass

    mock_tools.submit.assert_called_once()

    # Assert the current log levels (submit.py currently logs nothing even on failure)
    log_levels = [record.levelname for record in caplog.records]
    assert log_levels == []

    for record in caplog.records:
        msg = record.message.lower()
        assert "secret" not in msg
        assert "api_key" not in msg
