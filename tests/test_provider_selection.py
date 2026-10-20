import os
import pytest
from unittest.mock import patch
import importlib

def test_provider_configured():
    """Test when primary provider (OPENAI_MODEL) is configured."""
    env_vars = {
        "OPENAI_MODEL": "gpt-4o",
        "HUMBOLDT_MODEL": "llama-3",
        "PATH": os.environ.get("PATH", "")
    }
    with patch.dict(os.environ, env_vars, clear=True):
        import humboldt
        importlib.reload(humboldt)
        parser = humboldt.build_parser()
        args = parser.parse_args([])
        assert args.model == "gpt-4o"

def test_provider_fallback():
    """Test fallback to HUMBOLDT_MODEL when OPENAI_MODEL is unavailable."""
    env_vars = {
        "HUMBOLDT_MODEL": "llama-3",
        "PATH": os.environ.get("PATH", "")
    }
    with patch.dict(os.environ, env_vars, clear=True):
        import humboldt
        importlib.reload(humboldt)
        parser = humboldt.build_parser()
        args = parser.parse_args([])
        assert args.model == "llama-3"

def test_provider_unavailable_defaults():
    """Test default fallback when no providers are configured."""
    env_vars = {
        "PATH": os.environ.get("PATH", "")
    }
    with patch.dict(os.environ, env_vars, clear=True):
        import humboldt
        importlib.reload(humboldt)
        parser = humboldt.build_parser()
        args = parser.parse_args([])
        assert args.model == "Phi-4-mini-cpu-int4-rtn-block-32-acc-level-4-onnx"

def test_webchat_provider_configured():
    env_vars = {
        "OPENAI_MODEL": "gpt-4o",
        "HUMBOLDT_MODEL": "llama-3",
        "PATH": os.environ.get("PATH", "")
    }
    with patch.dict(os.environ, env_vars, clear=True):
        import webchat
        importlib.reload(webchat)
        assert webchat.MODEL_NAME == "gpt-4o"

def test_webchat_provider_fallback():
    env_vars = {
        "HUMBOLDT_MODEL": "llama-3",
        "PATH": os.environ.get("PATH", "")
    }
    with patch.dict(os.environ, env_vars, clear=True):
        import webchat
        importlib.reload(webchat)
        assert webchat.MODEL_NAME == "llama-3"

def test_webchat_provider_unavailable_defaults():
    env_vars = {
        "PATH": os.environ.get("PATH", "")
    }
    with patch.dict(os.environ, env_vars, clear=True):
        import webchat
        importlib.reload(webchat)
        assert webchat.MODEL_NAME == "Phi-4-mini-cpu-int4-rtn-block-32-acc-level-4-onnx"

def test_geoai_cli_provider_configured():
    env_vars = {
        "OPENAI_MODEL": "gpt-4o",
        "HUMBOLDT_MODEL": "llama-3",
        "PATH": os.environ.get("PATH", "")
    }
    with patch.dict(os.environ, env_vars, clear=True):
        import geoai_cli
        importlib.reload(geoai_cli)
        parser = geoai_cli._build_parser()
        args = parser.parse_args(["chat"])
        assert args.model == "gpt-4o"

def test_geoai_cli_provider_fallback():
    env_vars = {
        "HUMBOLDT_MODEL": "llama-3",
        "PATH": os.environ.get("PATH", "")
    }
    with patch.dict(os.environ, env_vars, clear=True):
        import geoai_cli
        importlib.reload(geoai_cli)
        parser = geoai_cli._build_parser()
        args = parser.parse_args(["chat"])
        assert args.model == "llama-3"

def test_geoai_cli_provider_unavailable_defaults():
    env_vars = {
        "PATH": os.environ.get("PATH", "")
    }
    with patch.dict(os.environ, env_vars, clear=True):
        import geoai_cli
        importlib.reload(geoai_cli)
        parser = geoai_cli._build_parser()
        args = parser.parse_args(["chat"])
        assert args.model == "Phi-4-mini-cpu-int4-rtn-block-32-acc-level-4-onnx"
