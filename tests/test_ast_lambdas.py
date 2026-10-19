import ast
import glob

def test_no_lambda_assignments():
    """Ensure lambda expressions are not assigned directly to names."""
    allowlist = {}

    files_to_check = glob.glob("*.py") + glob.glob("plugins/*.py")

    errors = []

    for filepath in files_to_check:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        try:
            tree = ast.parse(content, filename=filepath)
        except SyntaxError as e:
            errors.append(f"Syntax error in {filepath}: {e}")
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                # Check if the right-hand side is a Lambda
                if isinstance(node.value, ast.Lambda):
                    # Check if the target is an ast.Name
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            line_no = node.lineno

                            # Check against allowlist
                            allowed_lines = allowlist.get(filepath, [])
                            if line_no not in allowed_lines:
                                errors.append(
                                    f"{filepath}:{line_no}: Direct assignment of a lambda to a name (use 'def' instead)."
                                )

            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.value, ast.Lambda):
                    if isinstance(node.target, ast.Name):
                        line_no = node.lineno

                        allowed_lines = allowlist.get(filepath, [])
                        if line_no not in allowed_lines:
                            errors.append(
                                f"{filepath}:{line_no}: Direct assignment of a lambda to a name (use 'def' instead)."
                            )

    assert not errors, "\n".join(errors)
