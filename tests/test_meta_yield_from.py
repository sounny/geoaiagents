import ast
import glob
import pytest

def check_file_for_yield_from(filepath):
    try:
        with open(filepath, 'r') as f:
            tree = ast.parse(f.read(), filename=filepath)
    except SyntaxError:
        return []

    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            has_yield_from = False
            for stmt in node.body:
                for child in ast.walk(stmt):
                    if isinstance(child, ast.YieldFrom):
                        has_yield_from = True
                        break
                if has_yield_from:
                    break

            if has_yield_from:
                for handler in node.handlers:
                    catches_general = False
                    if handler.type is None:
                        catches_general = True
                    elif isinstance(handler.type, ast.Name):
                        if handler.type.id in ('Exception', 'BaseException'):
                            catches_general = True
                    elif isinstance(handler.type, ast.Tuple):
                        for elt in handler.type.elts:
                            if isinstance(elt, ast.Name) and elt.id in ('Exception', 'BaseException'):
                                catches_general = True

                    if catches_general:
                        has_raise = False
                        for handler_stmt in handler.body:
                            for child in ast.walk(handler_stmt):
                                if isinstance(child, ast.Raise):
                                    has_raise = True
                                    break
                            if has_raise:
                                break
                        if not has_raise:
                            offenders.append(node.lineno)
    return offenders

ALLOWLIST = {
    # Add files here if any existing code needs to be exempted
}

def test_no_yield_from_in_try_catch_without_reraise():
    """
    Ensure no yield from expressions occur inside a try/except block
    that catches BaseException or Exception without re-raising.
    """
    files_to_check = glob.glob("*.py") + glob.glob("plugins/*.py")

    failures = []
    for filepath in files_to_check:
        # Ignore tests and this specific meta test
        if filepath.startswith("tests/") or filepath.startswith("test_"):
            continue

        offenders = check_file_for_yield_from(filepath)

        if filepath in ALLOWLIST:
            # Check if all offenders are in the allowlist
            allowed_lines = ALLOWLIST[filepath]
            unallowed_offenders = [lineno for lineno in offenders if lineno not in allowed_lines]
            if unallowed_offenders:
                failures.append(f"{filepath}: Lines {unallowed_offenders}")
        elif offenders:
            failures.append(f"{filepath}: Lines {offenders}")

    if failures:
        pytest.fail(
            "Found yield from inside try/except catching BaseException/Exception without re-raising:\n" +
            "\n".join(failures)
        )
