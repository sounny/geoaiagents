import ast
import glob
import os

def test_no_large_bool_ops():
    # Base directory relative to this test file
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    files = []
    for pattern in ["*.py", "plugins/*.py"]:
        files.extend(glob.glob(os.path.join(base_dir, pattern)))

    count = 0
    offenders = {}

    allowlist = {}

    for filepath in files:
        filename = os.path.relpath(filepath, base_dir)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.BoolOp):
                    if len(node.values) > 4:
                        if filename not in allowlist or node.lineno not in allowlist[filename]:
                            count += 1
                            if filename not in offenders:
                                offenders[filename] = []
                            offenders[filename].append(node.lineno)
        except Exception:
            pass

    assert count == 0, f"Found {count} boolean expressions with more than four operands not in allowlist: {offenders}"
