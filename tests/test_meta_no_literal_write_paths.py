import ast
import glob
import os
import pytest

ALLOWLIST = {
    # No existing offenders currently found in the main repository, but the instruction asks to
    # parse every tests/test_*.py file and allowlist current offenders.
}

def test_no_literal_write_paths():
    """
    Ensures that test files do not contain open(..., "w"/"a"/"wb") calls
    where the path argument is a plain string literal rather than derived
    from tmp_path, tmpdir, or tempfile.
    """
    offenders = []

    # We test every file in the tests/ directory matching test_*.py
    for filepath in glob.glob("tests/test_*.py"):
        if filepath in ALLOWLIST:
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if getattr(node.func, "id", None) == "open":
                    # open() requires at least one argument (the file),
                    # mode can be the second positional arg, or a keyword arg 'mode'
                    mode_val = "r" # Default is "r"
                    path_is_literal = False

                    if len(node.args) >= 1:
                        # Check if path is a string literal
                        if isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                            path_is_literal = True

                    for kw in node.keywords:
                        if kw.arg == "file":
                            if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                                path_is_literal = True

                    if len(node.args) >= 2:
                        if isinstance(node.args[1], ast.Constant) and isinstance(node.args[1].value, str):
                            mode_val = node.args[1].value

                    for kw in node.keywords:
                        if kw.arg == "mode":
                            if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                                mode_val = kw.value.value

                    is_write_mode = any(c in mode_val for c in ("w", "a", "x", "+"))

                    if path_is_literal and is_write_mode:
                        offenders.append(f"{filepath}:{node.lineno}")

    assert not offenders, f"Found open(..., write_mode) with literal paths in tests: {', '.join(offenders)}"
