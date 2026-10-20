import ast
import tokenize
import glob
import re
import pytest

ALLOWLIST = {}

def test_todo_fixme_comments():
    files_to_check = glob.glob("*.py") + glob.glob("plugins/*.py")

    total_offenders = 0
    offender_counts = {}

    for filepath in files_to_check:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
            # Ensure the file is valid Python by parsing it with ast
            ast.parse(source, filename=filepath)
        except Exception:
            continue

        with open(filepath, "rb") as f:
            tokens = tokenize.tokenize(f.readline)
            for tok in tokens:
                if tok.type == tokenize.COMMENT:
                    text = tok.string
                    if 'TODO' in text or 'FIXME' in text:
                        # Find all occurrences of TODO or FIXME
                        for match in re.finditer(r'\b(TODO|FIXME)\b', text):
                            # The requirement: "fails counts TODO/FIXME comments that lack a (name) or issue reference"
                            if not re.search(r'\([^)]+\)', text) and not re.search(r'(?i)(#\d+|issue\b)', text):
                                offender_counts[filepath] = offender_counts.get(filepath, 0) + 1
                                total_offenders += 1
                                break

    # Verify against allowlist
    expected_total = sum(ALLOWLIST.values())
    assert total_offenders <= expected_total, f"Total offenders {total_offenders} exceeds baseline {expected_total}. Offender counts: {offender_counts}"
