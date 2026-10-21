import ast
import glob

# Allowlist for existing offenders: {"filename.py": [line_number1, line_number2]}
ALLOWLIST = {}

def test_no_type_equality_comparison():
    """
    Ensure top-level .py modules and plugins/*.py do not compare using type(x) == Y, type(x) != Y, type(x) is Y, or type(x) is not Y.
    They should use isinstance() instead.
    """
    files = glob.glob("*.py") + glob.glob("plugins/*.py")
    offenders = []

    for filepath in files:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()

        try:
            tree = ast.parse(source, filename=filepath)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Compare):
                # We need to correctly handle chained comparisons.
                # In ast.Compare, left is the first operand. comparators is the list of subsequent operands.
                # ops is the list of operations.
                for i, op in enumerate(node.ops):
                    left_operand = node.left if i == 0 else node.comparators[i-1]

                    if isinstance(left_operand, ast.Call) and isinstance(left_operand.func, ast.Name) and left_operand.func.id == "type":
                        if isinstance(op, (ast.Eq, ast.NotEq, ast.Is, ast.IsNot)):
                            if filepath in ALLOWLIST and node.lineno in ALLOWLIST[filepath]:
                                continue

                            comparator = node.comparators[i]
                            y_name = "Y"
                            if isinstance(comparator, ast.Name):
                                y_name = comparator.id
                            elif isinstance(comparator, ast.Attribute):
                                y_name = comparator.attr

                            if isinstance(op, ast.Eq):
                                op_str = "=="
                            elif isinstance(op, ast.NotEq):
                                op_str = "!="
                            elif isinstance(op, ast.Is):
                                op_str = "is"
                            else:
                                op_str = "is not"

                            offenders.append(
                                f"{filepath}:{node.lineno} - Found `type(x) {op_str} {y_name}`. Use isinstance(x, {y_name}) instead."
                            )

    if offenders:
        error_msg = "Found type comparisons (type(x) == Y, type(x) != Y, type(x) is Y, or type(x) is not Y). Please use isinstance() instead:\n"
        error_msg += "\n".join(offenders)
        assert False, error_msg
