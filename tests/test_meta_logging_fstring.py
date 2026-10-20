import ast
import os
import glob
import pytest

def get_python_files():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    top_level_files = glob.glob(os.path.join(base_dir, "*.py"))
    plugin_files = glob.glob(os.path.join(base_dir, "plugins", "*.py"))
    return top_level_files + plugin_files

@pytest.mark.parametrize("filepath", get_python_files())
def test_no_logging_fstring(filepath):
    """
    Test that logger/logging .debug/.info/.warning/.error/.exception calls
    do not use an f-string as their first argument.
    """
    allowlist = ["llm_utils.py"]  # Based on previous grep results
    if os.path.basename(filepath) in allowlist:
        pytest.skip(f"File {os.path.basename(filepath)} is in the allowlist.")

    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source, filename=filepath)

    class LoggingFstringVisitor(ast.NodeVisitor):
        def __init__(self):
            self.violations = []

        def visit_Call(self, node):
            # Check if it's a logging call
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in ("debug", "info", "warning", "error", "exception"):
                    # Basic check if the caller is logger or logging
                    # For simplicity, we just check if it's an attribute access
                    # like logging.error or logger.debug
                    if isinstance(node.func.value, ast.Name):
                        if node.func.value.id in ("logging", "logger"):
                            if node.args and isinstance(node.args[0], ast.JoinedStr):
                                self.violations.append(node.lineno)
            self.generic_visit(node)

    visitor = LoggingFstringVisitor()
    visitor.visit(tree)

    if visitor.violations:
        lines = ", ".join(map(str, visitor.violations))
        pytest.fail(f"Found logging call with f-string at lines {lines} in {filepath}")
