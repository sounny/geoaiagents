import ast
import glob

def test_no_long_sleep_calls():
    """
    AST-based meta-test to ensure no test file calls time.sleep() or sleep()
    with a literal argument > 0.5 seconds.
    """
    allowlist = set()  # Add allowlist for current offenders if any

    offenders = []

    for filepath in glob.glob("tests/test_*.py"):
        if filepath in allowlist:
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        try:
            tree = ast.parse(content, filename=filepath)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                is_sleep = False
                if isinstance(node.func, ast.Attribute):
                    if getattr(node.func.value, 'id', '') == 'time' and node.func.attr == 'sleep':
                        is_sleep = True
                elif isinstance(node.func, ast.Name):
                    if node.func.id == 'sleep':
                        is_sleep = True

                if is_sleep:
                    if node.args:
                        arg = node.args[0]
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, (int, float)):
                            if arg.value > 0.5:
                                offenders.append(f"{filepath}:{node.lineno}")

    assert not offenders, f"time.sleep() > 0.5s calls found in tests: {offenders}"
