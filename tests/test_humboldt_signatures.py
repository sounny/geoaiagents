import inspect
import pytest
from humboldt import (
    check_and_install_dependencies,
    is_package_installed,
    build_parser,
    handle_direct_command,
    execute_tool_loop,
    chat_loop,
    main
)

def test_humboldt_signatures():
    expected_signatures = {
        'check_and_install_dependencies': [],
        'is_package_installed': [('package_name', inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.empty)],
        'build_parser': [],
        'handle_direct_command': [
            ('user_input', inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.empty),
            ('tool_registry', inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.empty)
        ],
        'execute_tool_loop': [
            ('client', inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.empty),
            ('args', inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.empty),
            ('messages', inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.empty),
            ('functions', inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.empty),
            ('run_tool_call', inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.empty)
        ],
        'chat_loop': [
            ('client', inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.empty),
            ('args', inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.empty),
            ('messages', inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.empty),
            ('tool_registry', inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.empty),
            ('functions', inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.empty),
            ('run_tool_call', inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.empty)
        ],
        'main': []
    }

    functions_to_test = {
        'check_and_install_dependencies': check_and_install_dependencies,
        'is_package_installed': is_package_installed,
        'build_parser': build_parser,
        'handle_direct_command': handle_direct_command,
        'execute_tool_loop': execute_tool_loop,
        'chat_loop': chat_loop,
        'main': main
    }

    for name, func in functions_to_test.items():
        sig = inspect.signature(func)
        params = list(sig.parameters.values())
        expected_params = expected_signatures[name]

        assert len(params) == len(expected_params), f"Mismatch in number of parameters for {name}"

        for i, (expected_name, expected_kind, expected_default) in enumerate(expected_params):
            assert params[i].name == expected_name, f"Parameter name mismatch for {name}"
            assert params[i].kind == expected_kind, f"Parameter kind mismatch for {name}"
            assert params[i].default == expected_default, f"Parameter default mismatch for {name}"
