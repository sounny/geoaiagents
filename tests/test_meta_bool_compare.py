import ast
import glob
import sys

def test_no_bool_comparison():
    files = glob.glob("*.py") + glob.glob("plugins/*.py")

    # Pre-calculated allowlist for current offenders
    allowlist = {}

    offenders = {}

    def is_bool_constant(node):
        if isinstance(node, ast.Constant) and type(node.value) is bool:
            return True
        if sys.version_info < (3, 8) and hasattr(ast, 'NameConstant') and isinstance(node, getattr(ast, 'NameConstant')) and type(node.value) is bool:
            return True
        return False

    for filename in files:
        if filename.startswith("test_") or filename.startswith("tests/"):
            continue

        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        try:
            tree = ast.parse(content, filename=filename)
        except SyntaxError:
            continue

        count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Compare):
                left = node.left
                for op, comp in zip(node.ops, node.comparators):
                    if isinstance(op, (ast.Eq, ast.NotEq)):
                        if is_bool_constant(comp) or is_bool_constant(left):
                            count += 1
                    left = comp

        if count > 0:
            offenders[filename] = count

    for filename, count in offenders.items():
        allowed = allowlist.get(filename, 0)
        assert count <= allowed, (
            f"{filename} has {count} boolean comparisons (== True/False or != True/False), "
            f"expected at most {allowed}."
        )
