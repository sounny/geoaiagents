import ast
import glob
from pathlib import Path

# Allowlist of existing text-mode open() calls without encoding=
# (filepath, line_number)
ALLOWLIST = {
    ("humboldt.py", 26),
    ("install_requirements.py", 18),
}

def test_no_new_text_mode_open_without_encoding():
    files = glob.glob("*.py") + glob.glob("plugins/*.py")
    offenders = []

    for filepath in files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            tree = ast.parse(content, filename=filepath)
        except Exception:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "open":
                    has_encoding = False
                    is_binary = False

                    # Check keyword arguments for encoding= and mode=
                    for keyword in node.keywords:
                        if keyword.arg == "encoding":
                            has_encoding = True
                        elif keyword.arg == "mode":
                            if isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
                                if "b" in keyword.value.value:
                                    is_binary = True

                    # Check positional arguments for mode
                    if len(node.args) >= 2:
                        mode_arg = node.args[1]
                        if isinstance(mode_arg, ast.Constant) and isinstance(mode_arg.value, str):
                            if "b" in mode_arg.value:
                                is_binary = True

                    # If it's a text-mode open without encoding
                    if not has_encoding and not is_binary:
                        if (filepath, node.lineno) not in ALLOWLIST:
                            offenders.append((filepath, node.lineno))

    # We assert that the list of new offenders is empty.
    # We do not assert exact count of allowlist to avoid brittleness if allowlist shrinks.
    assert not offenders, f"New text-mode open() calls without encoding= found: {offenders}"
