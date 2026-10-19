import ast
import os
import glob
import pytest

# Allowlist: list of tuples (filename, function_name)
ALLOWLIST = [
    # Example: ("geoai_cli.py", "hashlib.md5")
]

def get_python_files():
    files = glob.glob("*.py")
    if os.path.exists("plugins"):
        files.extend(glob.glob("plugins/*.py"))
    return files

class HashlibVisitor(ast.NodeVisitor):
    def __init__(self, filename):
        self.filename = filename
        self.errors = []

    def visit_Call(self, node):
        func = node.func
        func_name = None

        # Check for hashlib.md5 or hashlib.sha1
        if isinstance(func, ast.Attribute):
            if isinstance(func.value, ast.Name) and func.value.id == "hashlib":
                if func.attr in ("md5", "sha1"):
                    func_name = f"hashlib.{func.attr}"
        elif isinstance(func, ast.Name):
            if func.id in ("md5", "sha1"):
                func_name = func.id

        if func_name:
            # check usedforsecurity=False
            is_secure = False
            for keyword in node.keywords:
                if keyword.arg == "usedforsecurity":
                    if isinstance(keyword.value, ast.Constant) and keyword.value.value is False:
                        is_secure = True
                    break

            # check if allowed
            if not is_secure:
                if (os.path.basename(self.filename), func_name) in ALLOWLIST:
                     pass
                else:
                     self.errors.append(f"File {self.filename}:{node.lineno} calls {func_name} without usedforsecurity=False")

        self.generic_visit(node)

@pytest.mark.parametrize("filepath", get_python_files())
def test_no_insecure_hashlib(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=filepath)

    visitor = HashlibVisitor(filepath)
    visitor.visit(tree)

    assert not visitor.errors, "\n".join(visitor.errors)
