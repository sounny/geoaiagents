import ast
import glob
import os
import pytest

# Allowlist of files that are currently missing module docstrings
ALLOWLIST = {
    "file_loaders.py",
    "llm_utils.py",
    "submit.py",
    "test_humboldt_draft.py",
    "webchat.py",
}

def test_module_docstrings():
    # Gather all top-level .py files and plugins/*.py files
    top_level_files = glob.glob("*.py")
    plugin_files = glob.glob("plugins/*.py")
    all_files = top_level_files + plugin_files

    total_allowed = len(ALLOWLIST)
    total_offenders = 0
    offenders_list = []

    for file_path in all_files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

            # Skip empty files
            if not content.strip():
                continue

            try:
                tree = ast.parse(content)
            except SyntaxError:
                continue

            # Check if there is a module docstring
            if ast.get_docstring(tree) is None:
                total_offenders += 1
                offenders_list.append(file_path)

    new_offenders = [f for f in offenders_list if os.path.basename(f) not in ALLOWLIST]

    assert not new_offenders, (
        f"The following files are missing module docstrings and are not in the ALLOWLIST: "
        f"{', '.join(new_offenders)}"
    )

    assert total_offenders <= total_allowed, (
        f"Expected at most {total_allowed} modules without a module docstring, "
        f"found {total_offenders}. Current offenders: {', '.join(offenders_list)}. "
        f"Do not add new files without a module docstring."
    )
