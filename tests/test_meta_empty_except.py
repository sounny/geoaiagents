import ast
import glob
import os
import pytest

# Known offenders that are allowed to have empty exception handlers
ALLOWLIST = {
    "webchat.py",
}

def is_bare_or_exception(node: ast.ExceptHandler) -> bool:
    if node.type is None:
        return True

    # Check for `except Exception:`
    if isinstance(node.type, ast.Name) and node.type.id == "Exception":
        return True

    # Check for `except (ValueError, Exception):`
    if isinstance(node.type, ast.Tuple):
        for elt in node.type.elts:
            if isinstance(elt, ast.Name) and elt.id == "Exception":
                return True

    return False

def is_empty_handler(node: ast.ExceptHandler) -> bool:
    if len(node.body) != 1:
        return False

    stmt = node.body[0]
    if isinstance(stmt, ast.Pass):
        return True
    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and stmt.value.value is Ellipsis:
        return True

    return False

def test_no_empty_except_handlers():
    """
    Test that no top-level or plugin python files contain `except Exception:` or bare `except:`
    handlers whose body is only `pass` or `...`.
    """
    python_files = glob.glob("*.py") + glob.glob("plugins/*.py")
    offenders = []

    for filepath in python_files:
        basename = os.path.basename(filepath)
        if basename in ALLOWLIST:
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        try:
            tree = ast.parse(content, filename=filepath)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if is_bare_or_exception(node) and is_empty_handler(node):
                    offenders.append(f"{filepath}:{node.lineno}")

    if offenders:
        pytest.fail(
            "Found empty `except Exception:` or bare `except:` handlers (body is only `pass` or `...`) "
            "in the following files:\n" + "\n".join(offenders)
        )
