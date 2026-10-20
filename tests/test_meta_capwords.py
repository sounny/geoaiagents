import ast
import glob
import re

def test_class_names_are_capwords():
    """
    Ensure that all top-level .py files and plugins/*.py files
    have CapWords class names (no underscores, must start with capital letter).
    """
    files = glob.glob("*.py") + glob.glob("plugins/*.py")

    # Allowlist for existing offenders: {filename: [class_names]}
    allowlist = {}

    errors = []

    for f in files:
        with open(f, "r", encoding="utf-8") as file:
            try:
                tree = ast.parse(file.read(), filename=f)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        name = node.name
                        # Check CapWords formatting
                        if not re.match(r"^[A-Z][a-zA-Z0-9]*$", name):
                            if f in allowlist and name in allowlist[f]:
                                continue
                            errors.append(f"{f}: {name}")
            except Exception as e:
                errors.append(f"Failed to parse {f}: {e}")

    assert not errors, f"Classes with non-CapWords names found:\n" + "\n".join(errors)
