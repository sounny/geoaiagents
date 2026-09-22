import os
import argparse
import pytest
from importlib import import_module
from unittest.mock import patch

def test_humboldt_cli_args(mocker):
    # Mocking os.environ to test default arguments
    env_vars = {"PATH": os.environ.get("PATH", "")}
    with patch.dict(os.environ, env_vars, clear=True):
        import humboldt
        parser = humboldt.build_parser()
        args = parser.parse_args([])
        assert args.base_url == "http://localhost:5272/v1/"
        assert args.api_key == "unused"
        assert args.model == "Phi-4-mini-cpu-int4-rtn-block-32-acc-level-4-onnx"

def test_humboldt_cli_args_with_env(mocker):
    # Mocking os.environ to test environment overrides
    env_vars = {
        "OPENAI_BASE_URL": "https://api.openai.com/v1/",
        "OPENAI_API_KEY": "test-key",
        "OPENAI_MODEL": "gpt-4o",
        "PATH": os.environ.get("PATH", "")
    }
    with patch.dict(os.environ, env_vars, clear=True):
        import humboldt
        import importlib
        importlib.reload(humboldt)
        parser = humboldt.build_parser()
        args = parser.parse_args([])
        assert args.base_url == "https://api.openai.com/v1/"
        assert args.api_key == "test-key"
        assert args.model == "gpt-4o"

def test_geoai_cli_args_with_env(mocker):
    env_vars = {
        "OPENAI_BASE_URL": "https://api.openai.com/v1/",
        "OPENAI_API_KEY": "test-key-cli",
        "OPENAI_MODEL": "gpt-4-turbo",
        "PATH": os.environ.get("PATH", "")
    }
    with patch.dict(os.environ, env_vars, clear=True):
        import geoai_cli
        parser = geoai_cli._build_parser()
        args = parser.parse_args(["chat"])
        assert args.base_url == "https://api.openai.com/v1/"
        assert args.api_key == "test-key-cli"
        assert args.model == "gpt-4-turbo"

def test_webchat_env(mocker):
    env_vars = {
        "OPENAI_BASE_URL": "https://custom.api/v1/",
        "OPENAI_API_KEY": "test-key-web",
        "OPENAI_MODEL": "gpt-3.5-turbo",
        "PATH": os.environ.get("PATH", "")
    }
    with patch.dict(os.environ, env_vars, clear=True):
        import webchat
        import importlib
        importlib.reload(webchat)
        assert webchat.BASE_URL == "https://custom.api/v1/"
        assert webchat.API_KEY == "test-key-web"
        assert webchat.MODEL_NAME == "gpt-3.5-turbo"


def test_plugin_loading_with_env(mocker):
    # Mock a fake plugin module to test if the registry loads it
    import sys
    from types import ModuleType
    import tool_registry

    mock_plugin = ModuleType("fake_plugin")

    def mock_register_tools(registry):
        registry.register_tool(
            name="fake_tool",
            description="Fake tool for testing",
            parameters={"type": "object", "properties": {}},
            handler=lambda x: "fake_result"
        )

    mock_plugin.register_tools = mock_register_tools
    sys.modules["fake_plugin"] = mock_plugin

    env_vars = {
        "GEOAI_PLUGIN_MODULES": "fake_plugin"
    }
    with patch.dict(os.environ, env_vars, clear=True):
        registry = tool_registry.create_registry()

        # Verify the fake tool was loaded
        assert "fake_tool" in registry._tools
        tool_def = registry._tools.get("fake_tool")
        assert tool_def is not None
        assert tool_def.handler({}) == "fake_result"

    # Clean up
    del sys.modules["fake_plugin"]
