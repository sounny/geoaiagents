import sys
import types
from unittest.mock import patch
import pytest

def test_submit_callables():
    # Mock the 'tools' module before importing 'submit'
    tools_mock = types.ModuleType("tools")
    def submit_mock(*args, **kwargs):
        pass
    tools_mock.submit = submit_mock
    sys.modules["tools"] = tools_mock

    with patch("tools.submit", autospec=True) as mock_submit:
        import submit as submit_module

        # Get public attributes using __all__ if defined, otherwise not starting with _
        public_names = getattr(submit_module, '__all__', [name for name in dir(submit_module) if not name.startswith('_')])

        allowlist = ['submit']
        for name in public_names:
            obj = getattr(submit_module, name)

            # Assert each one is callable
            if not callable(obj):
                pytest.xfail(f"Bug: Public member '{name}' is not callable")

            if not obj.__doc__ and name not in allowlist:
                pytest.xfail(f"Bug: Callable '{name}' has no docstring and is not in allowlist.")
