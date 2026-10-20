import ast
import glob

def test_no_invalid_dataclasses_replace_calls():
    files_to_check = glob.glob("*.py") + glob.glob("plugins/*.py")
    offenders = []
    allowlist = []  # Add files here if needed

    for filename in files_to_check:
        with open(filename, "r", encoding="utf-8") as f:
            source = f.read()

        try:
            tree = ast.parse(source, filename=filename)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                is_replace = False

                # Check for dataclasses.replace(...)
                if isinstance(func, ast.Attribute) and func.attr == "replace":
                    if isinstance(func.value, ast.Name) and func.value.id == "dataclasses":
                        is_replace = True

                # Check for replace(...) from from dataclasses import replace
                elif isinstance(func, ast.Name) and func.id == "replace":
                    is_replace = True

                if is_replace:
                    violation = False
                    if node.args:
                        first_arg = node.args[0]
                        if not isinstance(first_arg, ast.Name):
                            violation = True
                    else:
                        # replace() called with no arguments
                        violation = True

                    if violation:
                        offender_str = f"{filename}:{node.lineno}"
                        if offender_str not in allowlist:
                            offenders.append(offender_str)

    assert not offenders, (
        "Found dataclasses.replace() calls where the first argument is not a dataclass instance name (heuristic):\n" +
        "\n".join(offenders)
    )
