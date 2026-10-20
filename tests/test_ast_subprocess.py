import ast
import glob
import os
import pytest

ALLOWLIST = {"humboldt.py", "install_requirements.py"}

def test_no_unsafe_subprocess_run():
    files = glob.glob("*.py") + glob.glob("plugins/*.py")
    offenders = []

    for filepath in files:
        if os.path.basename(filepath) in ALLOWLIST:
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content, filename=filepath)

        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr == "run":
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "subprocess":
                        has_check = any(kw.arg == "check" for kw in node.keywords)
                        parent = getattr(node, "parent", None)

                        # If check is not specified and the result is not assigned
                        # (i.e. parent is an Expr node, meaning the return value is discarded),
                        # then the call is unsafe.
                        is_discarded = isinstance(parent, ast.Expr)

                        if not has_check and is_discarded:
                            offenders.append(f"{filepath}:{node.lineno}")

    assert not offenders, f"Found unsafe subprocess.run calls (must pass check= or capture result): {', '.join(offenders)}"
