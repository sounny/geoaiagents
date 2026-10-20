import ast
import glob

ALLOWLIST = {}

def test_open_called_inside_with_statement():
    files = glob.glob('*.py') + glob.glob('plugins/*.py')

    offenders = {}

    for filepath in files:
        if filepath.startswith('tests/'):
            continue

        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                tree = ast.parse(file.read(), filename=filepath)
        except SyntaxError:
            continue

        all_opens = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'open':
                all_opens.append(node)

        with_opens = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.With, ast.AsyncWith)):
                for item in node.items:
                    if isinstance(item.context_expr, ast.Call) and \
                       isinstance(item.context_expr.func, ast.Name) and \
                       item.context_expr.func.id == 'open':
                        with_opens.append(item.context_expr)

        non_with_count = sum(1 for node in all_opens if node not in with_opens)

        if non_with_count > 0:
            offenders[filepath] = non_with_count

    errors = []
    for filepath, count in offenders.items():
        allowed = ALLOWLIST.get(filepath, 0)
        if count > allowed:
            if allowed == 0:
                errors.append(f"{filepath} has {count} open() calls not used as a context manager.")
            else:
                errors.append(f"{filepath} has {count} open() calls not used as a context manager, exceeding its allowlisted baseline of {allowed}.")

    assert not errors, "open() called outside with statement:\n" + "\n".join(errors)
