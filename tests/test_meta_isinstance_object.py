import ast
import glob

# Allowlist for existing offenders: {"filename.py": [line_number1, line_number2]}
ALLOWLIST = {}

def test_no_isinstance_object():
    """
    Ensure top-level .py modules and plugins/*.py do not call isinstance(x, object)
    or isinstance(x, (..., object, ...)).
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
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "isinstance":
                    if len(node.args) == 2:
                        cls_arg = node.args[1]

                        is_offender = False

                        if isinstance(cls_arg, ast.Name) and cls_arg.id == "object":
                            is_offender = True
                        elif isinstance(cls_arg, ast.Tuple):
                            for elt in cls_arg.elts:
                                if isinstance(elt, ast.Name) and elt.id == "object":
                                    is_offender = True
                                    break

                        if is_offender:
                            if filepath in ALLOWLIST and node.lineno in ALLOWLIST[filepath]:
                                continue

                            offenders.append(
                                f"{filepath}:{node.lineno} - Found `isinstance(..., object)`. This is always true."
                            )

    if offenders:
        error_msg = "Found isinstance(..., object) calls which are always true:\n"
        error_msg += "\n".join(offenders)
        assert False, error_msg
