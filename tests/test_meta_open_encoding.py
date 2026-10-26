import ast
import glob
import os
import pytest

# Allowlist of files and the line numbers where text-mode open() calls without encoding= are permitted.
ALLOWLIST = {
    'humboldt.py': [27, 182],
    'humboldt.py': [26, 27, 182],
    "install_requirements.py": [18],
}

def get_python_files():
    top_level_files = glob.glob("*.py")
    plugin_files = glob.glob("plugins/*.py")
    return sorted(top_level_files + plugin_files)

@pytest.mark.parametrize("filepath", get_python_files())
def test_open_calls_have_encoding(filepath):
    """
    Ensure all text-mode open() calls pass an encoding= argument.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    tree = ast.parse(content, filename=filepath)
    offenders = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "open":
                # Check for encoding= keyword argument
                has_encoding = any(kw.arg == "encoding" for kw in node.keywords)
                if not has_encoding:
                    # Check if it's binary mode
                    is_binary = False

                    # Check positional arguments for mode
                    if len(node.args) >= 2:
                        mode_arg = node.args[1]
                        if isinstance(mode_arg, ast.Constant) and isinstance(mode_arg.value, str):
                            if "b" in mode_arg.value:
                                is_binary = True

                    # Check keyword arguments for mode
                    for kw in node.keywords:
                        if kw.arg == "mode":
                            if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                                if "b" in kw.value.value:
                                    is_binary = True

                    if not is_binary:
                        offenders.append(node.lineno)

    # Some files might be in subdirectories, so we use the basename for the allowlist
    # or the full path. The requirements just said allowlist. We'll use basename for simplicity,
    # as the filenames are unique enough in this small project.
    filename = os.path.basename(filepath)
    allowed_lines = ALLOWLIST.get(filename, [])

    unauthorized_offenders = [line for line in offenders if line not in allowed_lines]

    if unauthorized_offenders:
        pytest.fail(
            f"File {filepath} contains text-mode open() calls without encoding= at lines: "
            f"{unauthorized_offenders}. Please add encoding='utf-8' or add to allowlist."
        )
