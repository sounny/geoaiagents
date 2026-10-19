import ast
import glob

ALLOWLIST = []

def test_single_newline_eof():
    """
    Meta-test to ensure all top-level and plugins/*.py files end with exactly one newline.
    """
    python_files = glob.glob("*.py") + glob.glob("plugins/*.py")
    offenders = []

    for filepath in python_files:
        with open(filepath, "rb") as f:
            content = f.read()

        # Parse with ast as required by the meta-test rules
        ast.parse(content, filename=filepath)

        # Normalize line endings
        normalized = content.replace(b"\r\n", b"\n")

        has_one_newline = normalized.endswith(b"\n") and not normalized.endswith(b"\n\n")
        if not has_one_newline and filepath not in ALLOWLIST:
            offenders.append(filepath)

    assert not offenders, f"The following files do not end with exactly one newline: {offenders}"
