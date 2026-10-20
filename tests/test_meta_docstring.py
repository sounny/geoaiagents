import ast
import glob
import pytest
import os

ALLOWLIST = [
    "tool_registry.py::ToolDefinition",
    "tool_registry.py::ToolRegistry",
    "webchat.py::GradioLogHandler",
]

def get_python_files():
    files = glob.glob("*.py") + glob.glob("plugins/*.py")
    return [f for f in files if not f.startswith("test_") and f != "setup.py" and not f.startswith(".")]

@pytest.mark.parametrize("filepath", get_python_files())
def test_public_class_docstrings(filepath):
    with open(filepath, 'r') as file:
        try:
            tree = ast.parse(file.read(), filename=filepath)
        except SyntaxError:
            pytest.fail(f"Could not parse {filepath}")

    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if not node.name.startswith("_"):
                class_id = f"{os.path.basename(filepath)}::{node.name}"
                if class_id not in ALLOWLIST:
                    if not ast.get_docstring(node):
                        offenders.append(class_id)

    if offenders:
        pytest.fail(f"Public classes missing docstrings: {', '.join(offenders)}")
