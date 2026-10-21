import ast
import glob

ALLOWLIST = {}

def test_no_new_two_arg_getattr_string():
    files = glob.glob('*.py') + glob.glob('plugins/*.py')

    for filepath in files:
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read(), filename=filepath)
            except Exception:
                continue

        count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if getattr(node.func, 'id', '') == 'getattr':
                    if len(node.args) == 2 and not node.keywords:
                        arg2 = node.args[1]
                        is_constant_string = False

                        if isinstance(arg2, ast.Constant) and isinstance(arg2.value, str):
                            is_constant_string = True
                        elif hasattr(ast, 'Str') and isinstance(arg2, getattr(ast, 'Str', type(None))):
                            is_constant_string = True

                        if is_constant_string:
                            count += 1

        allowed = ALLOWLIST.get(filepath, 0)
        assert count <= allowed, (
            f"Found {count} getattr(x, 'name') calls with a constant string and no default argument in {filepath}! "
            f"Allowed: {allowed}. Please provide a default argument to getattr."
        )
