import ast
import glob
import os
import tokenize

def test_noqa_count():
    files_to_check = glob.glob('*.py') + glob.glob('plugins/*.py')

    allowlist = {
        'tool_registry.py': 2
    }

    total_noqa = 0
    total_allowed = sum(allowlist.values())

    for filepath in files_to_check:
        with open(filepath, 'rb') as f:
            content = f.read()

        # Parse with ast to ensure valid python as requested by the user.
        ast.parse(content, filename=filepath)

        # Count noqa comments
        noqa_count = 0
        with open(filepath, 'rb') as f:
            for tok in tokenize.tokenize(f.readline):
                if tok.type == tokenize.COMMENT and 'noqa' in tok.string.lower():
                    noqa_count += 1

        if noqa_count > 0:
            filename = os.path.basename(filepath)
            allowed = allowlist.get(filename, 0)
            assert noqa_count <= allowed, f"{filename} has {noqa_count} noqa comments, but only {allowed} are allowed."
            total_noqa += noqa_count

    assert total_noqa <= total_allowed, f"Total noqa count ({total_noqa}) exceeds allowed limit ({total_allowed})."
