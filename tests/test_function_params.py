import ast
import glob
import os
import pytest

# Known offenders that have more than 8 parameters.
# Format: {"filepath:function_name": 1}
ALLOWLIST = {
}

def get_python_files():
    # Top-level .py files
    files = glob.glob("*.py")
    # plugins/*.py files
    files.extend(glob.glob("plugins/*.py"))
    # filter files
    return [f for f in files if os.path.isfile(f) and not f.startswith("test_") and not f.startswith("tests/")]

def test_function_parameters():
    offenders = {}

    for filepath in get_python_files():
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()

        try:
            tree = ast.parse(source, filename=filepath)
        except SyntaxError:
            continue

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
                    key = f"{filepath}:{node.name}"
                    offenders[key] = offenders.get(key, 0) + 1

    total_offenders = sum(offenders.values())
    total_allowed = sum(ALLOWLIST.values())

    unallowed = []
    for key, count in offenders.items():
        if count > ALLOWLIST.get(key, 0):
            unallowed.append(f"{key}: {count}")

    if unallowed:
        pytest.fail(f"Functions have more than 8 parameters and are not in ALLOWLIST:\n" + "\n".join(unallowed))

    if total_offenders > total_allowed:
        pytest.fail(f"Total count of functions with > 8 parameters ({total_offenders}) exceeds the allowlisted baseline ({total_allowed}).")

    assert total_offenders <= total_allowed
