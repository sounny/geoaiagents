import ast
import glob
import pytest
from pathlib import Path

ALLOWLIST = set()

def get_python_files():
    top_level = glob.glob("*.py")
    plugins = glob.glob("plugins/*.py")
    return top_level + plugins

def is_warnings_ignore_call(node):
    if not isinstance(node, ast.Call):
        return False

    func = node.func
    is_target_func = False

    if isinstance(func, ast.Attribute):
        # warnings.filterwarnings or warnings.simplefilter
        if isinstance(func.value, ast.Name) and func.value.id == "warnings":
            if func.attr in ("filterwarnings", "simplefilter"):
                is_target_func = True
    elif isinstance(func, ast.Name):
        # filterwarnings or simplefilter
        if func.id in ("filterwarnings", "simplefilter"):
            is_target_func = True

    if not is_target_func:
        return False

    # Check if action is "ignore"
    if node.args:
        first_arg = node.args[0]
        if isinstance(first_arg, ast.Constant) and first_arg.value == "ignore":
            return True
        elif isinstance(first_arg, ast.Str) and first_arg.s == "ignore":
            return True

    for kw in node.keywords:
        if kw.arg == "action":
            if isinstance(kw.value, ast.Constant) and kw.value.value == "ignore":
                return True
            elif isinstance(kw.value, ast.Str) and kw.value.s == "ignore":
                return True

    return False

@pytest.mark.parametrize("filepath", get_python_files())
def test_no_warnings_ignore(filepath):
    if filepath in ALLOWLIST:
        return

    path = Path(filepath)
    if not path.is_file():
        return

    content = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(content, filename=filepath)
    except SyntaxError:
        pytest.fail(f"Could not parse {filepath}")

    offenders = []
    for node in ast.walk(tree):
        if is_warnings_ignore_call(node):
            offenders.append(str(node.lineno))

    if offenders:
        pytest.fail(
            f"File {filepath} contains warnings.filterwarnings('ignore') or "
            f"warnings.simplefilter('ignore') at line(s): {', '.join(offenders)}. "
            f"If intentional, add it to the ALLOWLIST in tests/test_meta_warnings_ignore.py."
        )
