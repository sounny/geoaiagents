import ast
import glob
import os

ALLOWLIST = {}

def test_meta_os_path_join():
    """
    Ensure the number of `os.path.join` calls in top-level Python modules
    and plugins doesn't grow beyond the current count.
    """
    def count_os_path_join(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read(), filename=filepath)
            except SyntaxError:
                return 0

        count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr == 'join':
                    if isinstance(node.func.value, ast.Attribute) and node.func.value.attr == 'path':
                        if isinstance(node.func.value.value, ast.Name) and node.func.value.value.id == 'os':
                            count += 1
        return count

    # Make sure we're searching relative to the root dir, not the cwd
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    files = glob.glob(os.path.join(root_dir, '*.py')) + glob.glob(os.path.join(root_dir, 'plugins', '*.py'))

    total_count = 0
    offenders = {}

    for f in files:
        # Normalize the file path to be relative to the root dir for consistency
        rel_f = os.path.relpath(f, root_dir)
        c = count_os_path_join(f)
        if c > 0:
            offenders[rel_f] = c
            total_count += c

    total_allowlist = sum(ALLOWLIST.values())

    # Check that no new offenders were introduced
    current_offenders = {f: c for f, c in offenders.items() if c > ALLOWLIST.get(f, 0)}

    assert not current_offenders, f"Found new os.path.join calls in: {current_offenders}"
    assert total_count <= total_allowlist, (
        f"Total os.path.join count ({total_count}) exceeded allowlist count ({total_allowlist}). "
    )
