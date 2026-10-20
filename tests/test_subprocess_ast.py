import ast
import glob
import pytest

# Allowlist for existing offenders: format is "filename:lineno"
# Example: "install_requirements.py:42"
ALLOWLIST = set()

def test_no_subprocess_string_literal_args():
    files_to_check = glob.glob('*.py') + glob.glob('plugins/*.py')

    errors = []
    for filepath in files_to_check:
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read(), filename=filepath)
            except SyntaxError as e:
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                is_subprocess_call = False

                # Check for subprocess.run, subprocess.Popen, etc.
                if isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "subprocess":
                        if node.func.attr in {"run", "call", "check_call", "check_output", "Popen"}:
                            is_subprocess_call = True

                if is_subprocess_call and node.args:
                    first_arg = node.args[0]
                    is_string_literal = False

                    if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
                        is_string_literal = True
                    elif isinstance(first_arg, ast.JoinedStr):
                        is_string_literal = True

                    if is_string_literal:
                        offender_id = f"{filepath}:{node.lineno}"
                        if offender_id not in ALLOWLIST:
                            errors.append(
                                f"{filepath}:{node.lineno}: subprocess call uses a string literal or f-string "
                                f"as its first argument instead of a list."
                            )

    if errors:
        pytest.fail("Found subprocess calls with string literals as the first argument instead of lists:\n" + "\n".join(errors))
