import ast
from pathlib import Path

def is_generic_handler(handler: ast.ExceptHandler) -> bool:
    if handler.type is None:
        return True
    if isinstance(handler.type, ast.Name) and handler.type.id in ('Exception', 'BaseException'):
        return True
    if isinstance(handler.type, ast.Tuple):
        for elt in handler.type.elts:
            if isinstance(elt, ast.Name) and elt.id in ('Exception', 'BaseException'):
                return True
    return False

def test_no_except_exception_before_specific():
    base_dir = Path(__file__).parent.parent.parent
    py_files = list(base_dir.glob("*.py")) + list((base_dir / "plugins").glob("*.py"))

    allowlist = set()
    offenders = set()

    for file_path in py_files:
        try:
            tree = ast.parse(file_path.read_text(encoding='utf-8'), filename=str(file_path))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                found_generic = False
                for handler in node.handlers:
                    if is_generic_handler(handler):
                        found_generic = True
                    elif found_generic:
                        # We found a specific handler after a generic handler
                        offenders.add(file_path.name)
                        break

    assert offenders <= allowlist, f"Found files where Exception/BaseException comes before a more specific except handler: {offenders - allowlist}"
