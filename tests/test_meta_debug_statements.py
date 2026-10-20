import ast
import glob
import pytest

# Allowlist for files that are permitted to contain debug statements (e.g. scripts meant for debugging if any exist)
# Currently empty as no existing offenders were found, but we provide it as requested.
ALLOWLIST = [
    # "plugins/example_plugin.py",
]

def test_no_debug_statements():
    files_to_check = glob.glob("*.py") + glob.glob("plugins/*.py")
    offenses = []

    for filename in files_to_check:
        if filename in ALLOWLIST:
            continue

        with open(filename, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=filename)
            except SyntaxError as e:
                # If there's a syntax error in the file, we just skip it or log it.
                # Usually pytest itself will fail if it's a test file, or the app won't run.
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "breakpoint":
                    offenses.append(f"{filename}:{node.lineno} contains breakpoint() call")

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ("pdb", "ipdb"):
                        offenses.append(f"{filename}:{node.lineno} imports {alias.name}")

            elif isinstance(node, ast.ImportFrom):
                if node.module in ("pdb", "ipdb"):
                    offenses.append(f"{filename}:{node.lineno} imports from {node.module}")

    assert not offenses, "Found debug statements (breakpoint, pdb, or ipdb):\n" + "\n".join(offenses)
