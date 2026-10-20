import ast
from pathlib import Path

# Allowlist: list of (filepath, function_name, line_number) tuples representing
# the currently known and permitted usages of hashlib.md5 or hashlib.sha1.
# Add to this list if new usages are genuinely required, but try to avoid them.
ALLOWLIST = []

def get_python_files():
    """Get all top-level .py files and .py files in plugins/ directory."""
    root_dir = Path(__file__).parent.parent
    files = list(root_dir.glob("*.py"))
    plugins_dir = root_dir / "plugins"
    if plugins_dir.exists():
        files.extend(list(plugins_dir.glob("*.py")))
    return files

def find_hashlib_weak_calls(filepath):
    """Parse the file and find uses of hashlib.md5 or hashlib.sha1."""
    root_dir = Path(__file__).parent.parent
    rel_path = str(filepath.relative_to(root_dir))

    with open(filepath, "r", encoding="utf-8") as f:
        try:
            source = f.read()
        except UnicodeDecodeError:
            return []

    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError:
        return []

    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Check for hashlib.md5() or hashlib.sha1()
            if isinstance(node.func, ast.Attribute) and getattr(node.func.value, "id", None) == "hashlib":
                if node.func.attr in ("md5", "sha1"):
                    offenders.append((rel_path, f"hashlib.{node.func.attr}", node.lineno))
            # Also check for from hashlib import md5, sha1; md5() / sha1()
            elif isinstance(node.func, ast.Name):
                if node.func.id in ("md5", "sha1"):
                    offenders.append((rel_path, node.func.id, node.lineno))

    return offenders

def test_hashlib_weak_hash_usage():
    """Meta-test to prevent the introduction of weak hashes like MD5 and SHA1."""
    files_to_check = get_python_files()

    all_offenders = []
    for filepath in files_to_check:
        offenders = find_hashlib_weak_calls(filepath)
        all_offenders.extend(offenders)

    # Check against allowlist
    unexpected_offenders = [
        offender for offender in all_offenders
        if offender not in ALLOWLIST
    ]

    if unexpected_offenders:
        error_msg = "Found unexpected uses of weak hashes (hashlib.md5 or hashlib.sha1):\n"
        for offender in unexpected_offenders:
            error_msg += f"- {offender[0]}:{offender[2]} used {offender[1]}\n"
        error_msg += f"\nCurrent total: {len(all_offenders)}. Allowed baseline: {len(ALLOWLIST)}."

        assert False, error_msg
