import ast
import glob

def test_no_duplicate_keys_in_dicts():
    """Fail if any top-level or plugin python module contains dict literals with repeated keys."""
    # Allowlist for files that already have this issue and we aren't changing right now
    allowlist = set()

    # Collect all top-level .py and plugins/*.py files
    files = glob.glob('*.py') + glob.glob('plugins/*.py')
    all_offenders = []

    for filepath in files:
        if filepath in allowlist:
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()

        try:
            tree = ast.parse(source, filename=filepath)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Dict):
                keys = []
                for key in node.keys:
                    if key is None:
                        continue # dict unpacking **kwargs

                    if isinstance(key, ast.Constant):
                        keys.append(key.value)
                    # Support for older python versions where ast.Constant is not always used for strings/numbers
                    elif type(key).__name__ == 'Str':
                        keys.append(key.s)
                    elif type(key).__name__ == 'Num':
                        keys.append(key.n)

                seen = set()
                for k in keys:
                    # In python dictionaries, keys are unique. In AST, we check if the literal key repeats
                    if k in seen:
                        all_offenders.append(f"{filepath}: duplicate key {repr(k)}")
                    seen.add(k)

    assert not all_offenders, "Duplicate dict keys found in literals:\n" + "\n".join(all_offenders)
