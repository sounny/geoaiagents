import ast
from pathlib import Path


def test_meta_comprehensions():
    """
    Ensure top-level Python modules and plugins (`plugins/*.py`) do not increase
    their count of comprehensions (list, set, dict, generator) with more than two `for` clauses
    beyond the current baseline, with an allowlist for current offenders.
    """
    project_root = Path(__file__).parent.parent
    top_level_files = list(project_root.glob("*.py"))
    plugin_files = list(project_root.glob("plugins/*.py"))
    files_to_check = top_level_files + plugin_files

    allowlist = {}

    total_allowed = sum(allowlist.values())
    total_found = 0
    new_offenders = []

    for file_path in files_to_check:
        try:
            tree = ast.parse(
                file_path.read_text(encoding="utf-8"), filename=str(file_path)
            )
        except SyntaxError:
            continue

        file_count = 0
        for node in ast.walk(tree):
            if isinstance(
                node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
            ):
                if len(node.generators) > 2:
                    file_count += 1

        rel_path = file_path.relative_to(project_root).as_posix()
        allowed_count = allowlist.get(rel_path, 0)

        if file_count > allowed_count:
            new_offenders.append(f"{rel_path}: {file_count} (allowed: {allowed_count})")

        total_found += file_count

    assert not new_offenders, (
        f"Found {total_found} comprehensions with >2 for clauses, "
        f"exceeding the baseline of {total_allowed}. New offenders:\n"
        + "\n".join(new_offenders)
    )
