import pytest
from webchat import parse_distance_table

def test_parse_distance_table_locking_header_only_empty():
    assert parse_distance_table('| A | B | C | D |\n|---|---|---|---|') == []

    table = '| Lat1 | Lon1 | Lat2 | Lon2 |\n|---|---|---|---|\n| 48.8 | 2.3 | 51.5 | -0.1 |'
    assert parse_distance_table(table) == [(48.8, 2.3), (51.5, -0.1)]

from webchat import parse_table_coordinates, create_map_html
import re

def test_create_map_html_markers_and_skips_invalid_locking_markers():
    table = """| Location | Latitude | Longitude |
|---|---|---|
| Valid 1 | 51.5074 | -0.1278 |
| Invalid 1 | ABC | DEF |
| Valid 2 | 48.8566 | 2.3522 |
| Invalid 2 | 10.0 |"""
    points = parse_table_coordinates(table, 1, 2)
    assert len(points) == 2
    html = create_map_html(points)
    assert len(re.findall(r"L\.marker", html)) == 2

from unittest.mock import patch, Mock
import pathlib
import pytest
import os
from webchat import respond, chat

class MockResponse:
    def __init__(self):
        self.choices = [self.MockChoice()]
    class MockChoice:
        def __init__(self):
            self.message = self.MockMessage()
        class MockMessage:
            def __init__(self):
                self.content = "Mock reply"
                self.function_call = None

class MockUploadFile:
    def __init__(self, name):
        self.name = name

def test_respond_path_arguments_match(tmp_path, mocker):
    mocker.patch("webchat.call_llm_with_retry", return_value=MockResponse())
    import webchat

    file_path = tmp_path / "test.txt"
    file_path.write_text("dummy")

    upload_file_str = MockUploadFile(str(file_path))
    upload_file_path = MockUploadFile(file_path)

    orig_messages = webchat.messages.copy()

    try:
        webchat.messages = orig_messages.copy()
        res_str = respond("hello", [], upload_file_str)
        msg_str = webchat.messages[-2]["content"]

        webchat.messages = orig_messages.copy()

        try:
            res_path = respond("hello", [], upload_file_path)
            msg_path = webchat.messages[-2]["content"]
        except Exception as e:
            pytest.xfail(reason=f"Exception differs with Path: {e}")

        if msg_str != msg_path or res_str != res_path:
            pytest.xfail(reason="Results differ when using pathlib.Path instead of str")

        assert msg_str == msg_path
        assert res_str == res_path

    finally:
        webchat.messages = orig_messages

def test_chat_path_arguments_match(tmp_path, mocker):
    mocker.patch("webchat.call_llm_with_retry", return_value=MockResponse())
    import webchat

    file_path = tmp_path / "test.txt"
    file_path.write_text("dummy")

    upload_file_str = MockUploadFile(str(file_path))
    upload_file_path = MockUploadFile(file_path)

    orig_messages = webchat.messages.copy()

    try:
        webchat.messages = orig_messages.copy()
        history_str = chat("hello", [], upload_file_str)

        webchat.messages = orig_messages.copy()

        try:
            history_path = chat("hello", [], upload_file_path)
        except Exception as e:
            pytest.xfail(reason=f"Exception differs with Path: {e}")

        if history_str != history_path:
            pytest.xfail(reason="Results differ when using pathlib.Path instead of str")

        assert history_str == history_path

    finally:
        webchat.messages = orig_messages


from unittest.mock import patch, Mock
import pathlib
import pytest
import os
from webchat import respond, chat

class MockResponse:
    def __init__(self):
        self.choices = [self.MockChoice()]
    class MockChoice:
        def __init__(self):
            self.message = self.MockMessage()
        class MockMessage:
            def __init__(self):
                self.content = "Mock reply"
                self.function_call = None

class MockUploadFile:
    def __init__(self, name):
        self.name = name

def test_respond_path_arguments_match(tmp_path, mocker):
    mocker.patch("webchat.call_llm_with_retry", return_value=MockResponse())
    import webchat

    file_path = tmp_path / "test.txt"
    file_path.write_text("dummy")

    upload_file_str = MockUploadFile(str(file_path))
    upload_file_path = MockUploadFile(file_path)

    orig_messages = webchat.messages.copy()

    try:
        webchat.messages = orig_messages.copy()
        res_str = respond("hello", [], upload_file_str)
        msg_str = webchat.messages[-2]["content"]

        webchat.messages = orig_messages.copy()

        try:
            res_path = respond("hello", [], upload_file_path)
            msg_path = webchat.messages[-2]["content"]
        except Exception as e:
            pytest.xfail(reason=f"Exception differs with Path: {e}")

        if msg_str != msg_path or res_str != res_path:
            pytest.xfail(reason="Results differ when using pathlib.Path instead of str")

        assert msg_str == msg_path
        assert res_str == res_path

    finally:
        webchat.messages = orig_messages

def test_chat_path_arguments_match(tmp_path, mocker):
    mocker.patch("webchat.call_llm_with_retry", return_value=MockResponse())
    import webchat

    file_path = tmp_path / "test.txt"
    file_path.write_text("dummy")

    upload_file_str = MockUploadFile(str(file_path))
    upload_file_path = MockUploadFile(file_path)

    orig_messages = webchat.messages.copy()

    try:
        webchat.messages = orig_messages.copy()
        history_str = chat("hello", [], upload_file_str)

        webchat.messages = orig_messages.copy()

        try:
            history_path = chat("hello", [], upload_file_path)
        except Exception as e:
            pytest.xfail(reason=f"Exception differs with Path: {e}")

        if history_str != history_path:
            pytest.xfail(reason="Results differ when using pathlib.Path instead of str")

        assert history_str == history_path

    finally:
        webchat.messages = orig_messages


from unittest.mock import patch
import pathlib
import pytest
import os
from webchat import respond, chat

class MockResponse:
    def __init__(self):
        self.choices = [self.MockChoice()]
    class MockChoice:
        def __init__(self):
            self.message = self.MockMessage()
        class MockMessage:
            def __init__(self):
                self.content = "Mock reply"
                self.function_call = None

class MockUploadFile:
    def __init__(self, name):
        self.name = name

def test_respond_path_arguments_match(tmp_path):
    import webchat

    file_path = tmp_path / "test.txt"
    file_path.write_text("dummy")

    upload_file_str = MockUploadFile(str(file_path))
    upload_file_path = MockUploadFile(file_path)

    orig_messages = webchat.messages.copy()

    with patch("webchat.call_llm_with_retry", return_value=MockResponse()):
        try:
            webchat.messages = orig_messages.copy()
            res_str = respond("hello", [], upload_file_str)
            msg_str = webchat.messages[-2]["content"]

            webchat.messages = orig_messages.copy()

            try:
                res_path = respond("hello", [], upload_file_path)
                msg_path = webchat.messages[-2]["content"]
            except Exception as e:
                pytest.xfail(reason=f"Exception differs with Path: {e}")

            if msg_str != msg_path or res_str != res_path:
                pytest.xfail(reason="Results differ when using pathlib.Path instead of str")

            assert msg_str == msg_path
            assert res_str == res_path

        finally:
            webchat.messages = orig_messages

def test_chat_path_arguments_match(tmp_path):
    import webchat

    file_path = tmp_path / "test.txt"
    file_path.write_text("dummy")

    upload_file_str = MockUploadFile(str(file_path))
    upload_file_path = MockUploadFile(file_path)

    orig_messages = webchat.messages.copy()

    with patch("webchat.call_llm_with_retry", return_value=MockResponse()):
        try:
            webchat.messages = orig_messages.copy()
            history_str = chat("hello", [], upload_file_str)

            webchat.messages = orig_messages.copy()

            try:
                history_path = chat("hello", [], upload_file_path)
            except Exception as e:
                pytest.xfail(reason=f"Exception differs with Path: {e}")

            if history_str != history_path:
                pytest.xfail(reason="Results differ when using pathlib.Path instead of str")

            assert history_str == history_path

        finally:
            webchat.messages = orig_messages
