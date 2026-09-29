import sys
import io
import pytest
from geoai_cli import _read_value_or_stdin

def test_read_value_or_stdin_with_dash(monkeypatch):
    monkeypatch.setattr(sys, "stdin", io.StringIO("test_stdin_data"))
    assert _read_value_or_stdin("-") == "test_stdin_data"

def test_read_value_or_stdin_with_normal_string(monkeypatch):
    assert _read_value_or_stdin("test_normal_string") == "test_normal_string"

def test_read_value_or_stdin_empty_string_tty(monkeypatch):
    mock_stdin = io.StringIO("")
    mock_stdin.isatty = lambda: True
    monkeypatch.setattr(sys, "stdin", mock_stdin)
    assert _read_value_or_stdin("") == ""

def test_read_value_or_stdin_empty_string_not_tty(monkeypatch):
    mock_stdin = io.StringIO("pipe_data")
    mock_stdin.isatty = lambda: False
    monkeypatch.setattr(sys, "stdin", mock_stdin)
    assert _read_value_or_stdin("") == "pipe_data"
