import ast
import glob
import pytest
from pathlib import Path

# Allowlist for files that currently have threading.Thread calls without a name= argument
# Mapping file path to number of un-named thread constructions
ALLOWLIST = {}

def get_python_files():
    base_dir = Path(__file__).parent.parent
    top_level = [str(p.relative_to(base_dir)) for p in base_dir.glob("*.py")]
    plugins = [str(p.relative_to(base_dir)) for p in base_dir.glob("plugins/*.py")]
    return top_level + plugins

def test_no_new_unnamed_threads():
    """
    Meta-test to ensure that top-level .py modules and plugins/*.py do not increase
    their count of threading.Thread(...) constructions that pass no name= argument
    beyond the current baseline.
    """
    target_files = get_python_files()

    total_unnamed = 0
    file_counts = {}
    total_allowed = sum(ALLOWLIST.values())

    base_dir = Path(__file__).parent.parent
    for file_path in target_files:
        path = base_dir / file_path
        if not path.is_file():
            continue

        try:
            content = path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=file_path)
        except SyntaxError as e:
            pytest.fail(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            pytest.fail(f"Failed to parse {file_path}: {e}")

        count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                is_thread = False
                if isinstance(node.func, ast.Attribute):
                    if getattr(node.func.value, 'id', '') == 'threading' and node.func.attr == 'Thread':
                        is_thread = True
                elif isinstance(node.func, ast.Name):
                    if node.func.id == 'Thread':
                        is_thread = True

                if is_thread:
                    has_name = any(kw.arg == 'name' for kw in node.keywords)
                    if not has_name:
                        count += 1

        if count > 0:
            file_counts[file_path] = count
            total_unnamed += count

    # Verify that no new offenders were introduced
    for file_path, count in file_counts.items():
        allowed_count = ALLOWLIST.get(file_path, 0)
        assert count <= allowed_count, (
            f"File {file_path} contains {count} threading.Thread(...) construction(s) without a 'name=' argument, "
            f"which exceeds the allowed baseline of {allowed_count}."
        )

    assert total_unnamed <= total_allowed, (
        f"Total number of unnamed thread constructions ({total_unnamed}) exceeds "
        f"the allowed baseline ({total_allowed})."
    )
