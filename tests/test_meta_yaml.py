import ast
import glob
from pathlib import Path

# Allowlist for files that currently use yaml.load without Loader=yaml.SafeLoader
ALLOWLIST = set()

def test_no_unsafe_yaml_load():
    """
    Ensure no top-level or plugin python module uses `yaml.load(...)`
    without explicitly passing `Loader=...`.
    """
    # Collect top-level .py and plugins/*.py files
    files_to_check = []
    files_to_check.extend(glob.glob("*.py"))
    files_to_check.extend(glob.glob("plugins/*.py"))

    offenders = []

    for file_path in files_to_check:
        path = Path(file_path)
        if not path.is_file():
            continue

        if file_path in ALLOWLIST:
            continue

        try:
            content = path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=file_path)
        except SyntaxError:
            # Skip files with syntax errors
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check if the function being called is yaml.load
                if isinstance(node.func, ast.Attribute) and node.func.attr == "load":
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "yaml":

                        # Check if Loader=... is provided
                        is_safe = False
                        for kw in node.keywords:
                            if kw.arg == "Loader":
                                is_safe = True
                                break

                        if not is_safe:
                            offenders.append(file_path)
                            break  # No need to find more in this file to mark it as an offender

    if offenders:
        msg = (
            "The following files contain `yaml.load` calls without `Loader=`. "
            "Prefer `yaml.safe_load` or pass `Loader=yaml.SafeLoader`:\n"
            + "\n".join(f"  - {f}" for f in offenders)
        )
        assert False, msg
