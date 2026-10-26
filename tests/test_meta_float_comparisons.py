import ast
import glob
import os

ALLOWLIST = {
    "test_dd2dms.py",
    "test_tool_registry.py",
    "test_geocode.py",
    "test_raster.py",
}

def _is_float_literal(node):
    """
    Checks if an AST node represents a float literal, handling negative
    float literals which are parsed as a UnaryOp(USub(), Constant).
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, float):
        return True
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        if isinstance(node.operand, ast.Constant) and isinstance(node.operand.value, float):
            return True
    return False

def test_no_float_eq_asserts():
    """
    Parses every test file in tests/test_*.py and ensures there are no
    assert statements comparing a float literal with ==.
    Such comparisons should use pytest.approx.
    """
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    test_files = glob.glob(os.path.join(tests_dir, "test_*.py"))
    assert test_files, "No test files found"

    violations = []

    for filepath in test_files:
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
            if isinstance(node, ast.Assert):
                if isinstance(node.test, ast.Compare):
                    has_eq = any(isinstance(op, ast.Eq) for op in node.test.ops)
                    if has_eq:
                        is_float_literal = False

                        # Check left side
                        if _is_float_literal(node.test.left):
                            is_float_literal = True

                        # Check comparators (right side of == and others if chained)
                        for comp in node.test.comparators:
                            if _is_float_literal(comp):
                                is_float_literal = True

                        if is_float_literal:
                            violations.append(f"{basename}:{node.lineno}")

    assert not violations, (
        f"Found assert statements comparing a float literal with ==. "
        f"Use pytest.approx instead. Violations: {', '.join(violations)}"
    )
