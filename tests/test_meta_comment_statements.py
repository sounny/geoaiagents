import ast
import glob
import os
import tokenize
import pytest

# Allowlist mapping filepath to the count of comment statements allowed.
# These files currently contain comments that parse as valid Python statements.
ALLOWLIST = {
    "install_requirements.py": 1,
    "dd2dms.py": 2,
}

def count_comment_statements(filepath: str) -> int:
    """Counts the number of comments in a file that can be parsed as valid Python statements."""
    count = 0
    try:
        with tokenize.open(filepath) as f:
            tokens = tokenize.generate_tokens(f.readline)
            for tok_type, tok_string, start, end, line in tokens:
                if tok_type == tokenize.COMMENT:
                    # Strip leading '#' and whitespace
                    comment_text = tok_string.lstrip('#').strip()
                    if not comment_text:
                        continue

                    try:
                        # Try to parse the comment as a python statement
                        parsed = ast.parse(comment_text)
                        # If it parses and produces actual statements (not just empty Module)
                        if parsed.body:
                            count += 1
                    except SyntaxError:
                        pass
    except Exception:
        pass

    return count

def test_no_new_comment_statements():
    """
    Ensure that we do not increase the number of commented-out Python statements.
    """
    files_to_check = glob.glob("*.py") + glob.glob("plugins/*.py")

    total_found = 0
    offenses = []

    for filepath in files_to_check:
        if not os.path.isfile(filepath):
            continue

        c = count_comment_statements(filepath)
        if c > 0:
            total_found += c
            allowed = ALLOWLIST.get(filepath, 0)
            if c > allowed:
                offenses.append(f"{filepath} has {c} comment statement(s) (allowed: {allowed})")

    allowed_total = sum(ALLOWLIST.values())

    assert total_found <= allowed_total, (
        f"Found {total_found} comment statements total, but only {allowed_total} are allowed.\n"
        + "\n".join(offenses)
    )
