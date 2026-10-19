import ast
import glob
import pytest

# Allowlist for files that currently use shell=True
ALLOWLIST = []

def get_python_files():
    """Returns a list of all top-level .py modules and plugins/*.py."""
    files = glob.glob("*.py")
    files.extend(glob.glob("plugins/*.py"))
    return sorted(list(set(files)))

@pytest.mark.parametrize("filepath", get_python_files())
def test_no_subprocess_shell_true(filepath):
    if filepath in ALLOWLIST:
        pytest.skip(f"{filepath} is in the allowlist for shell=True usage")

    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        pytest.fail(f"Could not parse {filepath} as valid Python code")

    offending_lines = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            has_shell_true = False
            for kw in node.keywords:
                if kw.arg == "shell":
                    if isinstance(kw.value, ast.Constant) and kw.value.value is True:
                        has_shell_true = True
                    elif isinstance(kw.value, ast.NameConstant) and kw.value.value is True:
                        has_shell_true = True

            if has_shell_true:
                offending_lines.append(node.lineno)

    if offending_lines:
        lines = ", ".join(map(str, offending_lines))
        pytest.fail(f"File {filepath} contains function calls with shell=True on line(s): {lines}")
