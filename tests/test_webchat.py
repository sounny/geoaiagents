import logging
from webchat import GradioLogHandler, parse_distance_table, log_history
import webchat

def test_gradio_log_handler_emit():
    # If the handler relies on a specific state of log_history, maybe it is a module-level variable
    handler = GradioLogHandler()
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname="", lineno=0,
        msg="test message", args=(), exc_info=None
    )

    # Save the current length of log_history
    initial_length = len(webchat.log_history)

    # Should not throw
    handler.emit(record)

    # Assert that the length has increased
    assert len(webchat.log_history) > initial_length

def test_parse_distance_table_malformed():
    assert parse_distance_table("This is not a table") == []
    assert parse_distance_table("Line1\nLine2\nLine3\nLine4") == []
