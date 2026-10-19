import ast
import glob

def test_no_star_imports():
    """
    Test that no top-level module or plugin uses 'from module import *'.
    Includes an allowlist for current offenders.
    """
    allowlist = []  # Add files here if they need an exception (e.g., 'plugins/old_plugin.py')

    files_to_check = glob.glob("*.py") + glob.glob("plugins/*.py")
    offenders = []

    for file_path in files_to_check:
        if file_path in allowlist:
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=file_path)
        except Exception as e:
            # If parsing fails for another reason, we might want to log it,
            # but usually it means invalid python code.
            print(f"Error parsing {file_path}: {e}")
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if any(alias.name == "*" for alias in node.names):
                    offenders.append(f"{file_path}:{node.lineno}")

    assert not offenders, f"Found 'from module import *' in the following files:\n" + "\n".join(offenders)
