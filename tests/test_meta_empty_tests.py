import ast
from pathlib import Path
import pytest

# Add any known test_*.py files that legitimately have no test functions here.
ALLOWLIST = set()

def get_test_files():
    """Yield all tests/test_*.py files in the project."""
    tests_dir = Path("tests")
    if not tests_dir.exists():
        return
    for path in tests_dir.rglob("test_*.py"):
        if path.is_file():
            yield path

@pytest.mark.parametrize("filepath", list(get_test_files()), ids=lambda p: str(p))
def test_file_has_test_functions(filepath: Path):
    """
    Ensure that every tests/test_*.py file actually defines at least one
    test function (def test_...) or test class (class Test...).
    """
    if filepath.name in ALLOWLIST:
        pytest.skip(f"File {filepath.name} is in the allowlist")

    content = filepath.read_text(encoding="utf-8")
    try:
        tree = ast.parse(content, filename=str(filepath))
    except SyntaxError as e:
        pytest.fail(f"SyntaxError when parsing {filepath}: {e}")

    has_test = False
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("test_"):
                has_test = True
                break
        elif isinstance(node, ast.ClassDef):
            if node.name.startswith("Test"):
                has_test = True
                break

    if not has_test:
        pytest.fail(
            f"Test file '{filepath}' defines no test_* function or Test* class. "
            "If this is intentional, add it to ALLOWLIST in this test."
        )
