import ast
import glob

ALLOWLIST = {}

def test_no_assert_string_literal():
    offenders = []

    files_to_check = glob.glob("*.py") + glob.glob("plugins/*.py")

    for file_path in files_to_check:
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=file_path)
            except SyntaxError:
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Assert):
                # Check if the test is a non-empty string literal
                if getattr(node.test, "value", None) is not None:
                    if isinstance(node.test, ast.Constant) and isinstance(node.test.value, str):
                        if node.test.value != "":
                            line_num = node.lineno
                            if file_path not in ALLOWLIST or line_num not in ALLOWLIST.get(file_path, []):
                                offenders.append(f"{file_path}:{line_num}")

    assert not offenders, f"Found assert statements with non-empty string literals (always true):\n" + "\n".join(offenders)
