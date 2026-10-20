import ast
from pathlib import Path
import pytest

# Baseline for modules currently exceeding the 800-line limit
EXPECTED_OFFENDERS = set()

def test_module_length_limit():
    root_dir = Path(__file__).parent.parent
    top_level_files = list(root_dir.glob("*.py"))
    plugin_files = list(root_dir.glob("plugins/*.py"))
    all_files = top_level_files + plugin_files

    long_modules = set()

    for file_path in all_files:
        content = file_path.read_text(encoding="utf-8")

        # Verify valid python via ast parsing
        ast.parse(content, filename=str(file_path))

        # Count lines
        num_lines = len(content.splitlines())

        if num_lines > 800:
            rel_path = file_path.relative_to(root_dir)
            long_modules.add(str(rel_path))

    new_offenders = long_modules - EXPECTED_OFFENDERS

    assert not new_offenders, f"New modules longer than 800 lines found: {new_offenders}"

    assert len(long_modules) <= len(EXPECTED_OFFENDERS), \
        f"Total modules longer than 800 lines ({len(long_modules)}) exceeds baseline ({len(EXPECTED_OFFENDERS)})"
