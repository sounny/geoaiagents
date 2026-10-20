import re
import glob
import os
import pytest

# Allowlist for blocks that are intentionally partial or might not compile on their own
# We match exact snippet string or a substring
ALLOWLIST = [
    "registry.register_tool(...)"
]

def test_markdown_python_snippets():
    # Find all top-level .md files
    md_files = glob.glob('*.md')

    assert len(md_files) > 0, "No markdown files found to check."

    for md_file in md_files:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract python code blocks
        blocks = re.findall(r'```python\s+(.*?)```', content, re.DOTALL)

        for i, block in enumerate(blocks):
            # Check if this block should be skipped due to allowlist
            if any(allowed in block for allowed in ALLOWLIST):
                continue

            try:
                compile(block, f"{md_file}:block_{i}", 'exec')
            except SyntaxError as e:
                pytest.fail(f"SyntaxError in {md_file} block {i}:\n\n{block}\n\nError: {e}")
            except Exception as e:
                pytest.fail(f"Compilation error in {md_file} block {i}:\n\n{block}\n\nError: {e}")
