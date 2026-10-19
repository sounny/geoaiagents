import ast
import os
import glob

# Allowlist for existing offenders
ALLOWLIST = []

def test_no_unsafe_tarfile_extraction():
    # Gather target python files: top-level and plugins/*.py
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_files = glob.glob(os.path.join(project_root, "*.py")) + glob.glob(os.path.join(project_root, "plugins", "*.py"))

    offenders = []

    for filepath in target_files:
        rel_filepath = os.path.relpath(filepath, project_root)
        if rel_filepath in ALLOWLIST:
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        try:
            tree = ast.parse(content, filename=filepath)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check if it's a method call for extractall or extract
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ("extractall", "extract"):
                        # Now check if it has a `filter` keyword argument
                        has_filter = any(
                            isinstance(kw, ast.keyword) and kw.arg == "filter"
                            for kw in node.keywords
                        )
                        if not has_filter:
                            offenders.append(f"{rel_filepath}:{node.lineno}")

    assert not offenders, "Found tarfile extractall() or extract() calls without filter= argument:\n" + "\n".join(offenders)
