import ast
from pathlib import Path
import pytest

# Add any known unused fixtures here
ALLOWLIST = set()

def test_no_unused_fixtures():
    """
    Ensure that no fixture defined in tests/ is unused.
    A fixture is considered unused if it is not autouse=True
    and it is not requested by name in any test or other fixture,
    or via @pytest.mark.usefixtures.
    """
    fixtures = []
    usages = set()

    for path in Path("tests").rglob("test_*.py"):
        try:
            content = path.read_text(encoding="utf-8")
            tree = ast.parse(content)
        except Exception as e:
            pytest.fail(f"Could not parse {path}: {e}")

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                is_fixture = False
                is_autouse = False

                # Check decorators for @pytest.fixture or @fixture
                for dec in node.decorator_list:
                    # @fixture
                    if isinstance(dec, ast.Name) and dec.id == "fixture":
                        is_fixture = True
                    # @pytest.fixture
                    elif isinstance(dec, ast.Attribute) and dec.attr == "fixture":
                        if isinstance(dec.value, ast.Name) and dec.value.id == "pytest":
                            is_fixture = True
                    # @fixture(...) or @pytest.fixture(...)
                    elif isinstance(dec, ast.Call):
                        func = dec.func
                        if isinstance(func, ast.Name) and func.id == "fixture":
                            is_fixture = True
                        elif isinstance(func, ast.Attribute) and func.attr == "fixture":
                            if isinstance(func.value, ast.Name) and func.value.id == "pytest":
                                is_fixture = True

                        if is_fixture:
                            for kw in dec.keywords:
                                if kw.arg == "autouse":
                                    if isinstance(kw.value, ast.Constant) and kw.value.value is True:
                                        is_autouse = True
                                    elif hasattr(ast, "NameConstant") and isinstance(kw.value, ast.NameConstant) and kw.value.value is True:
                                        is_autouse = True

                    # Check @pytest.mark.usefixtures on function
                    if isinstance(dec, ast.Call):
                        func = dec.func
                        if isinstance(func, ast.Attribute) and func.attr == "usefixtures":
                            if isinstance(func.value, ast.Name) and func.value.id == "pytest":
                                for arg in dec.args:
                                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                                        usages.add(arg.value)
                                    elif isinstance(arg, ast.Str):
                                        usages.add(arg.s)
                            elif isinstance(func.value, ast.Attribute) and func.value.attr == "mark":
                                if isinstance(func.value.value, ast.Name) and func.value.value.id == "pytest":
                                    for arg in dec.args:
                                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                                            usages.add(arg.value)
                                        elif isinstance(arg, ast.Str):
                                            usages.add(arg.s)

                if is_fixture:
                    fixtures.append((node.name, path.name, is_autouse))

                # Check parameters for usages
                # In ast, node.args contains arguments
                for arg in node.args.args:
                    usages.add(arg.arg)
                for arg in node.args.kwonlyargs:
                    usages.add(arg.arg)

            # Check @pytest.mark.usefixtures on class
            elif isinstance(node, ast.ClassDef):
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Call):
                        func = dec.func
                        if isinstance(func, ast.Attribute) and func.attr == "usefixtures":
                            if isinstance(func.value, ast.Name) and func.value.id == "pytest":
                                for arg in dec.args:
                                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                                        usages.add(arg.value)
                                    elif isinstance(arg, ast.Str):
                                        usages.add(arg.s)
                            elif isinstance(func.value, ast.Attribute) and func.value.attr == "mark":
                                if isinstance(func.value.value, ast.Name) and func.value.value.id == "pytest":
                                    for arg in dec.args:
                                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                                            usages.add(arg.value)
                                        elif isinstance(arg, ast.Str):
                                            usages.add(arg.s)

    unused_fixtures = []
    for name, filename, is_autouse in fixtures:
        if not is_autouse and name not in usages:
            if name not in ALLOWLIST:
                unused_fixtures.append(f"{name} in {filename}")

    if unused_fixtures:
        pytest.fail(
            f"Found unused fixtures (not autouse, not requested, not in allowlist): {unused_fixtures}"
        )
