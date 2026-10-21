import ast
from pathlib import Path
import pytest

# Baseline for modules currently exceeding the length limit
EXPECTED_OFFENDERS_800 = set()
EXPECTED_OFFENDERS_1500 = set()

@pytest.mark.parametrize("limit, expected_offenders", [
    (800, EXPECTED_OFFENDERS_800),
    (1500, EXPECTED_OFFENDERS_1500),
])
def test_module_length_limit(limit, expected_offenders):
    root_dir = Path(__file__).parent.parent
    top_level_files = list(root_dir.glob("*.py"))
    plugin_files = list(root_dir.glob("plugins/*.py"))
    all_files = top_level_files + plugin_files

    long_modules = set()

    for file_path in all_files:
        content = file_path.read_text(encoding="utf-8")

        # Verify valid python via ast parsing
        ast.parse(content, filename=str(file_path))

        # Count lines using the same logic as before so we don't change behavior
        num_lines = len(content.splitlines())

        if num_lines > limit:
            rel_path = file_path.relative_to(root_dir)
            long_modules.add(str(rel_path))

    new_offenders = long_modules - expected_offenders

    assert not new_offenders, f"New modules longer than {limit} lines found: {new_offenders}"

    assert len(long_modules) <= len(expected_offenders), \
        f"Total modules longer than {limit} lines ({len(long_modules)}) exceeds baseline ({len(expected_offenders)})"
