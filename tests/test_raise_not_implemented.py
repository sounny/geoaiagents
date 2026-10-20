import ast
import os
import pytest
from pathlib import Path

# Allowlist for existing offenders (if any). Currently empty.
ALLOWLIST = set()

def test_no_raise_not_implemented():
    root_dir = Path(__file__).resolve().parent.parent
    py_files = list(root_dir.glob("*.py")) + list((root_dir / "plugins").glob("*.py"))

    offenders = []

    for filepath in py_files:
        if filepath.name in ALLOWLIST:
            continue

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            tree = ast.parse(content, filename=str(filepath))

            for node in ast.walk(tree):
                if isinstance(node, ast.Raise):
                    if getattr(node, 'exc', None) is not None:
                        # Check for `raise NotImplemented`
                        if isinstance(node.exc, ast.Name) and node.exc.id == "NotImplemented":
                            offenders.append(filepath.name)
                        # Check for `raise NotImplemented(...)`
                        elif isinstance(node.exc, ast.Call) and isinstance(node.exc.func, ast.Name) and node.exc.func.id == "NotImplemented":
                            offenders.append(filepath.name)
        except SyntaxError:
            pass

    assert len(offenders) == 0, f"Found 'raise NotImplemented' in {offenders}. Use NotImplementedError instead."
