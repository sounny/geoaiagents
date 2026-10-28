import pytest
from tool_registry import parse_tool_args

@pytest.mark.xfail(raises=AssertionError, reason="parse_tool_args silently drops list inputs instead of parsing or validating them")
def test_parse_tool_args_list_with_duplicates():
    input_list = [{"location": "Paris"}, {"location": "Paris"}]
    result = parse_tool_args(input_list)
    assert result != {}, "Lists are silently discarded"
