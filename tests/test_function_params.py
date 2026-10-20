import ast
import glob
import pytest
import os

ALLOWLIST = {}

def get_python_files():
    # Top-level .py files
    files = glob.glob("*.py")
    # plugins/*.py files
    files.extend(glob.glob("plugins/*.py"))
    # filter files
    return [f for f in files if os.path.isfile(f)]

@pytest.mark.parametrize("filepath", get_python_files())
def test_function_parameters(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        pytest.skip(f"SyntaxError in {filepath}, skipping AST parse")
        return

    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Count the total number of arguments
            args = node.args
            num_params = len(args.posonlyargs) + len(args.args) + len(args.kwonlyargs)
            if args.vararg:
                num_params += 1
            if args.kwarg:
                num_params += 1

            if num_params > 8:
                if filepath in ALLOWLIST and node.name in ALLOWLIST[filepath]:
                    continue
                offenders.append(f"{node.name} (line {node.lineno}): {num_params} parameters")

    if offenders:
        pytest.fail(f"Functions in {filepath} have more than 8 parameters:\n" + "\n".join(offenders))
