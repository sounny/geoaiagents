import ast
import glob
import os
import pytest

# Allowlist of files that are currently missing module docstrings
ALLOWLIST = {
    "test_docs_snippets.py",
    "test_humboldt_draft.py",
    "submit.py",

    "test_docs_snippets.py",
    "test_humboldt_draft.py",
    "submit.py",

    "test_humboldt_draft.py",
    "submit.py",

    "webchat.py",
    "llm_utils.py",
    "file_loaders.py",
    "test_distance_issue.py",
}

def test_module_docstrings():
    # Gather all top-level .py files and plugins/*.py files
    top_level_files = glob.glob("*.py")
    plugin_files = glob.glob("plugins/*.py")
    all_files = top_level_files + plugin_files

    missing_docstrings = []

    for file_path in all_files:
        # Get just the filename for checking against the allowlist
        filename = os.path.basename(file_path)

        if filename in ALLOWLIST:
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

            # Skip empty files
            if not content.strip():
                continue

            tree = ast.parse(content)

            # Check if there is a module docstring
            if ast.get_docstring(tree) is None:
                missing_docstrings.append(file_path)

    assert not missing_docstrings, f"The following non-empty modules are missing module docstrings: {', '.join(missing_docstrings)}"
