import ast
import glob
import sys


def test_no_percent_string_formatting():
    files = glob.glob("*.py") + glob.glob("plugins/*.py")

    # Pre-calculated allowlist for current offenders
    # (There are currently no offenders in the codebase)
    allowlist = {}

    offenders = {}

    for filename in files:
        if filename.startswith("test_") or filename.startswith("tests/"):
            continue

        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()

        try:
            tree = ast.parse(content, filename=filename)
        except SyntaxError:
            continue

        count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
                if isinstance(node.left, ast.Constant) and isinstance(
                    node.left.value, str
                ):
                    count += 1
                elif (
                    sys.version_info < (3, 8)
                    and hasattr(ast, "Str")
                    and isinstance(node.left, getattr(ast, "Str"))
                ):
                    count += 1

        if count > 0:
            offenders[filename] = count

    for filename, count in offenders.items():
        allowed = allowlist.get(filename, 0)
        assert count <= allowed, (
            f"{filename} has {count} uses of % string formatting "
            f"on string literals, expected at most {allowed}."
        )
