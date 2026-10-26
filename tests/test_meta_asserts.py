import ast
import glob

def test_no_asserts_in_test_functions():
    offenders = []

    for filename in glob.glob('tests/test_*.py'):
        if filename == 'tests/test_meta_asserts.py':
            continue

        with open(filename, 'r') as f:
            tree = ast.parse(f.read(), filename=filename)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                has_assert = False
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.Assert):
                        has_assert = True
                        break
                    if isinstance(subnode, ast.Call):
                        # Check for pytest.raises or pytest.warns
                        if isinstance(subnode.func, ast.Attribute) and isinstance(subnode.func.value, ast.Name) and subnode.func.value.id == 'pytest':
                            if subnode.func.attr in ('raises', 'warns'):
                                has_assert = True
                                break
                        # Check for mock assert_* calls
                        if isinstance(subnode.func, ast.Attribute) and subnode.func.attr.startswith('assert_'):
                            has_assert = True
                            break

                if not has_assert:
                    offenders.append(f"{filename}::{node.name}")

    # Allowlist for existing offenders
    allowlist = [
        'tests/test_plugins_init.py::test_plugins_package_imports_cleanly',
    'tests/test_plugins_init.py::test_example_plugin_importable',
    'tests/test_meta_markers.py::test_pytest_markers_have_reasons',
    'tests/test_imports.py::test_modules_only_import_stdlib',
    'tests/test_meta_complexity.py::test_cyclomatic_complexity',
    'tests/test_pytest_config.py::test_pytest_pythonpath',
    'tests/test_meta_subprocess_shell.py::test_no_subprocess_shell_true',
    'tests/test_meta_all_defined.py::test_all_exports_defined',
    'tests/test_geohash.py::test_geohash_invalid',
    'tests/test_meta_skip.py::test_no_reasonless_skips',
    'tests/test_meta_yield_from.py::test_no_yield_from_in_try_catch_without_reraise',
    'tests/test_meta_mktemp.py::test_no_mktemp_calls',
    'tests/test_snake_case_names.py::test_snake_case_function_names',
    'tests/test_meta_empty_tests.py::test_file_has_test_functions',
    'tests/test_readme.py::test_readme_file_paths',
    'tests/test_meta_verify.py::test_no_verify_false_in_calls',
    'tests/test_no_globals.py::test_no_global_statements',
    'tests/test_meta_empty_except.py::test_no_empty_except_handlers',
    'tests/test_no_pickle.py::test_no_pickle_load',
    'tests/test_subprocess_ast.py::test_no_subprocess_string_literal_args',
    'tests/test_meta_open_path.py::test_meta_no_open_path_calls',
    'tests/test_meta_skip_reason.py::test_meta_no_skips_without_reason',
    'tests/test_gitignore.py::test_gitignore_entries',
    'tests/test_meta_logging_fstring.py::test_no_logging_fstring',
    'tests/test_meta_exit.py::test_no_sys_exit_outside_main',
    'tests/test_bbox.py::test_bbox_area',
    'tests/test_meta_no_os_chdir.py::test_no_os_chdir',
    'tests/test_function_params.py::test_function_parameters',
    'tests/test_meta_open_encoding.py::test_open_calls_have_encoding',
    'tests/test_chmod_meta.py::test_no_insecure_chmod',
    'tests/test_meta_class_method_count.py::test_class_method_count',
    'tests/test_unreachable.py::test_no_unreachable_code_after_control_flow',
    'tests/test_code_quality.py::test_no_bare_raise_outside_except',
    'tests/test_meta_docstring.py::test_public_class_docstrings',
    'tests/test_deprecated_imports.py::test_no_deprecated_imports',
    'tests/test_example_plugin.py::test_unknown_hook_safe',
    'tests/test_meta_del.py::test_no_del_in_classes',
    'tests/test_meta_secrets.py::test_no_hardcoded_secrets',
    'tests/test_agents_md.py::test_agents_md_paths_exist',
    'tests/test_nesting.py::test_control_flow_nesting_depth',
    'tests/test_import_order.py::test_isolated_import',
    'tests/test_crs.py::test_normalize_crs_valid',
    'tests/test_crs.py::test_normalize_crs_unknown',
    'tests/test_meta_input.py::test_no_input_calls_outside_main_or_cli',
    'tests/test_os_system_calls.py::test_no_os_system_or_popen',
    'tests/test_fstring_meta.py::test_no_empty_fstrings',
    'tests/test_index_html.py::test_index_html_mixed_content'
    'tests/test_meta_markers.py::test_pytest_markers_have_reasons',
    'tests/test_imports.py::test_modules_only_import_stdlib',
    'tests/test_meta_complexity.py::test_cyclomatic_complexity',
    'tests/test_pytest_config.py::test_pytest_pythonpath',
    'tests/test_meta_subprocess_shell.py::test_no_subprocess_shell_true',
    'tests/test_meta_all_defined.py::test_all_exports_defined',
    'tests/test_geohash.py::test_geohash_invalid',
    'tests/test_meta_skip.py::test_no_reasonless_skips',
    'tests/test_meta_yield_from.py::test_no_yield_from_in_try_catch_without_reraise',
    'tests/test_meta_mktemp.py::test_no_mktemp_calls',
    'tests/test_snake_case_names.py::test_snake_case_function_names',
    'tests/test_meta_empty_tests.py::test_file_has_test_functions',
    'tests/test_readme.py::test_readme_file_paths',
    'tests/test_meta_verify.py::test_no_verify_false_in_calls',
    'tests/test_no_globals.py::test_no_global_statements',
    'tests/test_meta_empty_except.py::test_no_empty_except_handlers',
    'tests/test_no_pickle.py::test_no_pickle_load',
    'tests/test_subprocess_ast.py::test_no_subprocess_string_literal_args',
    'tests/test_meta_open_path.py::test_meta_no_open_path_calls',
    'tests/test_meta_skip_reason.py::test_meta_no_skips_without_reason',
    'tests/test_gitignore.py::test_gitignore_entries',
    'tests/test_meta_logging_fstring.py::test_no_logging_fstring',
    'tests/test_meta_exit.py::test_no_sys_exit_outside_main',
    'tests/test_bbox.py::test_bbox_area',
    'tests/test_meta_no_os_chdir.py::test_no_os_chdir',
    'tests/test_function_params.py::test_function_parameters',
    'tests/test_meta_open_encoding.py::test_open_calls_have_encoding',
    'tests/test_chmod_meta.py::test_no_insecure_chmod',
    'tests/test_meta_class_method_count.py::test_class_method_count',
    'tests/test_unreachable.py::test_no_unreachable_code_after_control_flow',
    'tests/test_code_quality.py::test_no_bare_raise_outside_except',
    'tests/test_meta_docstring.py::test_public_class_docstrings',
    'tests/test_deprecated_imports.py::test_no_deprecated_imports',
    'tests/test_example_plugin.py::test_unknown_hook_safe',
    'tests/test_meta_del.py::test_no_del_in_classes',
    'tests/test_meta_secrets.py::test_no_hardcoded_secrets',
    'tests/test_agents_md.py::test_agents_md_paths_exist',
    'tests/test_nesting.py::test_control_flow_nesting_depth',
    'tests/test_import_order.py::test_isolated_import',
    'tests/test_crs.py::test_normalize_crs_valid',
    'tests/test_crs.py::test_normalize_crs_unknown',
    'tests/test_meta_input.py::test_no_input_calls_outside_main_or_cli',
    'tests/test_os_system_calls.py::test_no_os_system_or_popen',
    'tests/test_fstring_meta.py::test_no_empty_fstrings',
    'tests/test_index_html.py::test_index_html_mixed_content'
    ]

    missing_from_allowlist = [o for o in offenders if o not in allowlist]
    assert not missing_from_allowlist, f"Test functions without asserts found (not in allowlist): {missing_from_allowlist}"
