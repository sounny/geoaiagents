import ast
import glob
import itertools

# Allowlist for current offenders
ALLOWLIST = set()

def test_meta_exception_names():
    """
    Meta-test to parse every top-level .py module and plugins/*.py with ast
    and fails on classes that inherit from Exception or another *Error class
    but whose name does not end in Error or Exception, with an allowlist for current offenders.
    """
    files = list(itertools.chain(glob.glob("*.py"), glob.glob("plugins/*.py")))

    violations = []

    for filepath in files:
        if filepath in ALLOWLIST:
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()

        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                is_exception = False
                for base in node.bases:
                    name = None
                    if isinstance(base, ast.Name):
                        name = base.id
                    elif isinstance(base, ast.Attribute):
                        name = base.attr

                    if name == "Exception" or (name and name.endswith("Error")):
                        is_exception = True
                        break

                if is_exception:
                    if not (node.name.endswith("Error") or node.name.endswith("Exception")):
                        key = f"{filepath}:{node.name}"
                        if key not in ALLOWLIST:
                            violations.append(key)

    assert not violations, "Found exception classes not ending with Error or Exception:\n" + "\n".join(violations)
