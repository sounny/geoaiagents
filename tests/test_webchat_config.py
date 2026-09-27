import os
import importlib
import pytest
import sys

# Ensure root directory is in sys.path if not already, to allow importing webchat
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import webchat

@pytest.fixture
def clean_env():
    # Save original env
    original_env = os.environ.copy()

    # Remove any existing OPENAI_MODEL or HUMBOLDT_MODEL
    if "OPENAI_MODEL" in os.environ:
        del os.environ["OPENAI_MODEL"]
    if "HUMBOLDT_MODEL" in os.environ:
        del os.environ["HUMBOLDT_MODEL"]

    yield

    # Restore original env
    os.environ.clear()
    os.environ.update(original_env)

def test_model_name_default(clean_env):
    importlib.reload(webchat)
    assert webchat.MODEL_NAME == "Phi-4-mini-cpu-int4-rtn-block-32-acc-level-4-onnx"

def test_model_name_humboldt_model(clean_env):
    os.environ["HUMBOLDT_MODEL"] = "custom-humboldt-model"
    importlib.reload(webchat)
    assert webchat.MODEL_NAME == "custom-humboldt-model"

def test_model_name_openai_model_takes_precedence(clean_env):
    os.environ["HUMBOLDT_MODEL"] = "custom-humboldt-model"
    os.environ["OPENAI_MODEL"] = "custom-openai-model"
    importlib.reload(webchat)
    assert webchat.MODEL_NAME == "custom-openai-model"
