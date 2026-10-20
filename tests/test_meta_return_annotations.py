import ast
import glob
import pytest

def test_missing_return_annotations():
    """
    Parses every top-level .py module and plugins/*.py with ast and fails if there are public functions
    without a return type annotation, and fails if the total grows beyond the current count,
    with an allowlist for current offenders.
    """
    allowlist = {
        'dd2dms.py': ['dd_to_dms_value', 'format_dms', 'main'],
        'file_loaders.py': ['test_load_geojson_point', 'extract'],
        'geocode.py': ['get_coordinates', 'parse_locations', 'main'],
        'humboldt.py': ['check_and_install_dependencies', 'is_package_installed', 'build_parser', 'handle_direct_command', 'execute_tool_loop', 'chat_loop', 'main', 'run_tool_call'],
        'install_requirements.py': ['read_requirements', 'install_package', 'install_package_auto', 'install_all_requirements', 'main'],
        'llm_utils.py': ['call_llm_with_retry'],
        'plugins/example_plugin.py': ['register_tools', 'ping_api'],
        'webchat.py': ['respond', 'chat', 'build_ui', 'main'],
    }

    files = glob.glob('*.py') + glob.glob('plugins/*.py')
    total_allowed = sum(len(funcs) for funcs in allowlist.values())

    current_offenders_count = 0
    new_offenders = []

    for f in sorted(files):
        # We only want to check product code (top-level and plugins)
        if f.startswith('test_') or f in ('find_public_functions.py', 'script.py', 'setup.py', 'conftest.py'):
            continue

        with open(f, 'r', encoding='utf-8') as file:
            try:
                tree = ast.parse(file.read(), filename=f)
            except SyntaxError:
                continue

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith('_'):
                    if node.returns is None:
                        current_offenders_count += 1
                        if f not in allowlist or node.name not in allowlist[f]:
                            new_offenders.append(f"{f}::{node.name}")

    if new_offenders:
        pytest.fail(f"Found new public functions without return annotations: {new_offenders}")

    assert current_offenders_count <= total_allowed, (
        f"Total public functions without return annotations ({current_offenders_count}) "
        f"exceeds the allowed baseline ({total_allowed})."
    )
