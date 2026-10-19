import ast
import glob

ALLOWLIST = []

def test_no_tz_naive_datetime_now():
    """
    Parses every top-level .py module and plugins/*.py with ast and fails on
    datetime.utcnow() or datetime.now() calls without a tz argument,
    with an allowlist for current offenders.
    """
    files = glob.glob('*.py') + glob.glob('plugins/*.py')
    offenders = []

    for f in files:
        if f in ALLOWLIST:
            continue

        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()

        try:
            tree = ast.parse(content)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for datetime.now() or datetime.utcnow()
                if isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == 'datetime':
                        if node.func.attr == 'now':
                            has_tz = any(kw.arg == 'tz' for kw in node.keywords)
                            if not node.args and not has_tz:
                                offenders.append(f"{f}:{node.lineno}")
                        elif node.func.attr == 'utcnow':
                            offenders.append(f"{f}:{node.lineno}")

    assert not offenders, f"Found tz-naive datetime.now() or datetime.utcnow() calls: {', '.join(offenders)}"
