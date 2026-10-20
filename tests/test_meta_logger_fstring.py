import ast
import glob
import os

ALLOWLIST = {
    "llm_utils.py": 2
}

def test_no_new_fstring_loggers():
    """
    Meta-test to ensure no new usages of f-strings are introduced as the
    first argument to logger or logging calls (.debug, .info, .warning, .error, .exception).
    """
    files = glob.glob("*.py") + glob.glob("plugins/*.py")

    total_offenses = 0
    baseline = sum(ALLOWLIST.values())

    offending_details = []

    for filename in files:
        if not os.path.isfile(filename):
            continue

        try:
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
            tree = ast.parse(content, filename=filename)
        except Exception:
            continue

        file_offenses = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    # Check if it's logging.* or logger.* or self.logger.*
                    is_logger = False
                    if isinstance(node.func.value, ast.Name):
                        if node.func.value.id in ('logger', 'logging'):
                            is_logger = True
                    elif isinstance(node.func.value, ast.Attribute):
                        if node.func.value.attr in ('logger', 'logging'):
                            is_logger = True

                    if is_logger and node.func.attr in ('debug', 'info', 'warning', 'error', 'exception', 'critical'):
                        # Check if first argument is an f-string
                        if node.args and isinstance(node.args[0], ast.JoinedStr):
                            file_offenses += 1
                            offending_details.append(f"{filename}:{node.lineno}")

        total_offenses += file_offenses

    error_message = (
        f"Found {total_offenses} logger/logging calls with f-strings, "
        f"which exceeds the baseline of {baseline}.\n"
        f"Offenders:\n" + "\n".join(offending_details)
    )

    assert total_offenses <= baseline, error_message
