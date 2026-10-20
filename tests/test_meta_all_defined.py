import ast
import glob
import pytest

# Allowlist for modules that are current offenders
ALLOWLIST = []

def get_python_files():
    files = glob.glob("*.py") + glob.glob("plugins/*.py")
    # exclude meta files and test files
    return [f for f in files if not f.startswith("test_") and f != "conftest.py" and f != "pytest.ini"]

@pytest.mark.parametrize("filepath", get_python_files())
def test_all_exports_defined(filepath):
    if filepath in ALLOWLIST:
        pytest.skip(reason=f"{filepath} is in the allowlist for __all__ offender")

    with open(filepath, 'r', encoding='utf-8') as file:
        try:
            tree = ast.parse(file.read(), filename=filepath)
        except SyntaxError:
            pytest.fail(f"SyntaxError in {filepath}")
            return

    defined_names = set()
    all_names = None

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defined_names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    defined_names.add(target.id)
                    if target.id == '__all__':
                        if isinstance(node.value, (ast.List, ast.Tuple)):
                            all_names = []
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Constant):
                                    all_names.append(elt.value)
                                elif hasattr(ast, 'Str') and isinstance(elt, ast.Str):
                                    all_names.append(elt.s)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                defined_names.add(alias.asname or alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                defined_names.add(alias.asname or alias.name)

    if all_names is not None:
        undefined = set(all_names) - defined_names
        if undefined:
            pytest.fail(f"{filepath} defines __all__ with undefined names: {undefined}")
