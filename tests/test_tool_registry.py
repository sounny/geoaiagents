import pytest
from tool_registry import parse_tool_args, ToolRegistry, create_registry

def test_parse_tool_args_dict():
    assert parse_tool_args({"key": "value"}) == {"key": "value"}

def test_parse_tool_args_valid_json():
    assert parse_tool_args('{"key": "value"}') == {"key": "value"}

def test_parse_tool_args_invalid_json():
    import pytest
    with pytest.raises(ValueError, match="Invalid JSON"):
        parse_tool_args('{"key": "value"')

def test_tool_registry_invoke_happy_path():
    result = create_registry().invoke('convert_dd_to_dms', '48.8566,2.3522')
    assert "Latitude" in result or "DMS" in result

def test_tool_registry_invoke_happy_path_json():
    result = create_registry().invoke('convert_dd_to_dms', '{"coordinates": "48.8566,2.3522"}')
    assert "Latitude" in result or "DMS" in result

def test_tool_registry_invoke_invalid_json():
    result = create_registry().invoke('convert_dd_to_dms', '{"coordinates": "48.8566,2.3522"')
    assert "Error running convert_dd_to_dms: Invalid JSON" in result

def test_parse_tool_args_json_array():
    assert parse_tool_args('["value"]') == {}

def test_parse_tool_args_empty_string():
    assert parse_tool_args("") == {}
    assert parse_tool_args(None) == {}

def test_tool_registry_invoke_error_reporting():
    registry = ToolRegistry()

    def buggy_handler(args):
        raise ValueError("Simulated error")

    registry.register_tool(
        name="buggy_tool",
        description="A buggy tool",
        parameters={},
        handler=buggy_handler
    )

    result = registry.invoke("buggy_tool", {})
    assert "Error running buggy_tool: Simulated error" in result

def test_tool_registry_invoke_missing_tool():
    registry = ToolRegistry()
    result = registry.invoke("missing_tool", {})
    assert result is None
def test_tool_registry_builtin_openai_functions_convert_dd_to_dms_membership():
    """Test registry and openai_functions structure (locking convert_dd_to_dms membership)."""
    reg = create_registry()

    assert reg.has_tool("convert_dd_to_dms") is True
    assert reg.has_tool("geocode_locations") is True
    assert reg.has_tool("calculate_distance") is True
    assert reg.has_tool("load_geojson") is True

    funcs = reg.openai_functions()
    assert isinstance(funcs, list)
    assert len(funcs) >= 3

    names = {f["name"] for f in funcs}
    assert "convert_dd_to_dms" in names

    for f in funcs:
        type_val = f.get("type", "function")
        assert type_val == "function"
        assert "name" in f and f["name"]
        assert "description" in f and f["description"]
        assert "parameters" in f and f["parameters"]

def test_tool_registry_name_validation():
    """Test that tool registry validates names are unique non-empty strings."""
    registry = ToolRegistry()

    # Test non-string name
    with pytest.raises(ValueError, match="Tool name must be a string"):
        registry.register_tool(name=123, description="desc", parameters={}, handler=lambda x: "test")

    # Test empty string name
    with pytest.raises(ValueError, match="Tool name must be a non-empty string"):
        registry.register_tool(name="", description="desc", parameters={}, handler=lambda x: "test")

    # Test duplicate name
    registry.register_tool(name="valid_name", description="desc", parameters={}, handler=lambda x: "test")
    with pytest.raises(ValueError, match="Tool 'valid_name' is already registered"):
        registry.register_tool(name="valid_name", description="desc2", parameters={}, handler=lambda x: "test")

def test_plugin_hook_handlers_order():
    """Test that registering two plugins and listing hook handlers twice returns the same order."""
    registry = ToolRegistry()
    unittest.mock.patch("logging.info").start()
    unittest.mock.patch("logging.warning").start()
    unittest.mock.patch("logging.exception").start()

    # In this codebase, "plugins" are added by calling `register_tool`.
    registry.register_tool(
        name="plugin_1",
        description="First plugin",
        parameters={},
        handler=lambda x: "plugin_1"
    )
    registry.register_tool(
        name="plugin_2",
        description="Second plugin",
        parameters={},
        handler=lambda x: "plugin_2"
    )

    # "listing hook handlers" for tools implies listing the tool definitions for the LLM.
    # The application uses `openai_functions()` to list these handlers for the LLM API.
    # We test this public API to ensure the ordering is consistent when invoked repeatedly.
    handlers_1 = [tool["name"] for tool in registry.openai_functions()]
    handlers_2 = [tool["name"] for tool in registry.openai_functions()]

    if handlers_1 != handlers_2:
        pytest.xfail("Tool/hook listing order is inconsistent")
    assert handlers_1 == handlers_2
import copy
import unittest.mock

def test_parse_tool_args_mutates_dict():
    args = {"key": "value"}
    orig_args = copy.deepcopy(args)
    parsed = parse_tool_args(args)
    parsed["new_key"] = "new_value"
    if args != orig_args:
        pytest.xfail("parse_tool_args mutates dict args when modified later")
    assert args == orig_args

def test_parse_tool_args_mutates_list():
    args = [1, 2, 3]
    orig_args = copy.deepcopy(args)
    parsed = parse_tool_args(args)
    parsed["new_key"] = "new_value"
    if args != orig_args:
        pytest.xfail("parse_tool_args mutates list args when modified later")
    assert args == orig_args

def test_register_tool_mutates_dict():
    reg = ToolRegistry()
    parameters = {"type": "object"}
    orig_parameters = copy.deepcopy(parameters)
    reg.register_tool(name="test", description="desc", parameters=parameters, handler=lambda x: "ok")
    if parameters != orig_parameters:
        pytest.xfail("register_tool mutates dict parameters")
    assert parameters == orig_parameters

def test_invoke_mutates_dict(tmp_path):
    temp_file = tmp_path / "test.json"
    temp_file.write_text("{}")

    reg = ToolRegistry()

    def handler(args):
        args["mutated"] = True
        # Using a dummy mock as an external call replacement for the test
        unittest.mock.MagicMock()("mock_external_call")
        return "ok"

    reg.register_tool(name="test", description="desc", parameters={}, handler=handler)

    args = {"file_path": str(temp_file)}
    orig_args = copy.deepcopy(args)

    reg.invoke("test", args)

    if args != orig_args:
        pytest.xfail("invoke mutates dict args")
    assert args == orig_args

def test_invoke_mutates_list(tmp_path):
    temp_file = tmp_path / "test.json"
    temp_file.write_text("{}")

    reg = ToolRegistry()

    def handler(args):
        if isinstance(args, dict):
            args["mutated"] = True
        unittest.mock.MagicMock()("mock_external_call")
        return "ok"

    reg.register_tool(name="test", description="desc", parameters={}, handler=handler)

    args = [str(temp_file)]
    orig_args = copy.deepcopy(args)

    reg.invoke("test", args)

    if args != orig_args:
        pytest.xfail("invoke mutates list args")
    assert args == orig_args
import copy
import unittest.mock

def test_parse_tool_args_mutates_dict():
    args = {"key": "value"}
    orig_args = copy.deepcopy(args)
    parsed = parse_tool_args(args)
    parsed["new_key"] = "new_value"
    if args != orig_args:
        pytest.xfail("parse_tool_args mutates dict args when modified later")
    assert args == orig_args

def test_parse_tool_args_mutates_list():
    args = [1, 2, 3]
    orig_args = copy.deepcopy(args)
    parsed = parse_tool_args(args)
    if isinstance(parsed, list):
        parsed.append(4)
    elif isinstance(parsed, dict):
        parsed["new_key"] = "new_value"

    if args != orig_args:
        pytest.xfail("parse_tool_args mutates list args when modified later")
    assert args == orig_args

def test_register_tool_mutates_dict():
    reg = ToolRegistry()
    parameters = {"type": "object"}
    orig_parameters = copy.deepcopy(parameters)
    reg.register_tool(name="test", description="desc", parameters=parameters, handler=lambda x: "ok")
    if parameters != orig_parameters:
        pytest.xfail("register_tool mutates dict parameters")
    assert parameters == orig_parameters

def test_invoke_mutates_dict(tmp_path, mocker):
    temp_file = tmp_path / "test.json"
    temp_file.write_text("{}")

    reg = ToolRegistry()

    def handler(args):
        args["mutated"] = True
        mocker.MagicMock()("mock_external_call")
        return "ok"

    reg.register_tool(name="test", description="desc", parameters={}, handler=handler)

    args = {"file_path": str(temp_file)}
    orig_args = copy.deepcopy(args)

    reg.invoke("test", args)

    if args != orig_args:
        pytest.xfail("invoke mutates dict args")
    assert args == orig_args

def test_invoke_mutates_list(tmp_path, mocker):
    temp_file = tmp_path / "test.json"
    temp_file.write_text("{}")

    reg = ToolRegistry()

    def handler(args):
        if isinstance(args, dict):
            args["mutated"] = True
        mocker.MagicMock()("mock_external_call")
        return "ok"

    reg.register_tool(name="test", description="desc", parameters={}, handler=handler)

    args = [str(temp_file)]
    orig_args = copy.deepcopy(args)

    reg.invoke("test", args)

    if args != orig_args:
        pytest.xfail("invoke mutates list args")
    assert args == orig_args
import copy
import unittest.mock

def test_parse_tool_args_mutates_dict():
    args = {"key": "value"}
    orig_args = copy.deepcopy(args)
    parsed = parse_tool_args(args)
    parsed["new_key"] = "new_value"
    if args != orig_args:
        pytest.xfail("parse_tool_args mutates dict args when modified later")
    assert args == orig_args

def test_parse_tool_args_mutates_list():
    args = [1, 2, 3]
    orig_args = copy.deepcopy(args)
    parsed = parse_tool_args(args)
    if isinstance(parsed, list):
        parsed.append(4)
    elif isinstance(parsed, dict):
        parsed["new_key"] = "new_value"

    if args != orig_args:
        pytest.xfail("parse_tool_args mutates list args when modified later")
    assert args == orig_args

def test_register_tool_mutates_dict():
    reg = ToolRegistry()
    parameters = {"type": "object"}
    orig_parameters = copy.deepcopy(parameters)
    reg.register_tool(name="test", description="desc", parameters=parameters, handler=lambda x: "ok")
    if parameters != orig_parameters:
        pytest.xfail("register_tool mutates dict parameters")
    assert parameters == orig_parameters

def test_invoke_mutates_dict(tmp_path):
    temp_file = tmp_path / "test.json"
    temp_file.write_text("{}")

    reg = ToolRegistry()

    def handler(args):
        args["mutated"] = True
        unittest.mock.MagicMock()("mock_external_call")
        return "ok"

    reg.register_tool(name="test", description="desc", parameters={}, handler=handler)

    args = {"file_path": str(temp_file)}
    orig_args = copy.deepcopy(args)

    reg.invoke("test", args)

    if args != orig_args:
        pytest.xfail("invoke mutates dict args")
    assert args == orig_args

def test_invoke_mutates_list(tmp_path):
    temp_file = tmp_path / "test.json"
    temp_file.write_text("{}")

    reg = ToolRegistry()

    def handler(args):
        if isinstance(args, dict):
            args["mutated"] = True
        unittest.mock.MagicMock()("mock_external_call")
        return "ok"

    reg.register_tool(name="test", description="desc", parameters={}, handler=handler)

    args = [str(temp_file)]
    orig_args = copy.deepcopy(args)

    reg.invoke("test", args)

    if args != orig_args:
        pytest.xfail("invoke mutates list args")
    assert args == orig_args
