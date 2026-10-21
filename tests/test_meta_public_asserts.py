import ast
import glob
import os

ALLOWLIST = {
    'file_loaders.py::test_load_geojson_point',
    'test_humboldt_draft.py::test_build_parser',
    'test_humboldt_draft.py::test_is_package_installed_error',
    'test_humboldt_draft.py::test_is_package_installed_found',
    'test_humboldt_draft.py::test_is_package_installed_not_found',
}

def test_no_asserts_in_public_functions():
    """
    Parses every top-level .py module and plugins/*.py with ast and fails on
    assert statements inside public functions outside tests, with an allowlist.
    """
    files = [f for f in glob.glob('*.py') if os.path.isfile(f)] + \
            [f for f in glob.glob('plugins/*.py') if os.path.isfile(f)]

    assert files, "No top-level or plugin python files found"

    offenders = []

    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read(), filename=file)
            except SyntaxError:
                continue

        # Traverse AST and find public functions/methods
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith('_'):
                    has_assert = any(isinstance(subnode, ast.Assert) for subnode in ast.walk(node))
                    if has_assert:
                        offenders.append(f"{file}::{node.name}")
            elif isinstance(node, ast.ClassDef):
                if not node.name.startswith('_'):
                    for class_node in node.body:
                        if isinstance(class_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            if not class_node.name.startswith('_'):
                                has_assert = any(isinstance(subnode, ast.Assert) for subnode in ast.walk(class_node))
                                if has_assert:
                                    offenders.append(f"{file}::{node.name}::{class_node.name}")

    missing_from_allowlist = [o for o in offenders if o not in ALLOWLIST]

    assert not missing_from_allowlist, (
        f"Found assert statements in public functions (not in allowlist): {missing_from_allowlist}"
    )
