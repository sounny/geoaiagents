import ast
import glob
import pytest

# Allowlist for existing offenders:
# Format: (filepath, node_type, name)
# Note: we currently don't have any offenders found, but the allowlist is here.
ALLOWLIST = set([
    # e.g., ("some_module.py", "function_name", "type"),
])

def _get_names_from_target(target):
    names = []
    if isinstance(target, ast.Name):
        names.append(target.id)
    elif isinstance(target, (ast.Tuple, ast.List)):
        for elt in target.elts:
            names.extend(_get_names_from_target(elt))
    elif isinstance(target, ast.Starred):
        names.extend(_get_names_from_target(target.value))
    return names

def check_shadowing(filepath):
    builtins_list = {'list', 'dict', 'id', 'type', 'input', 'str', 'sum', 'file'}
    offenders = []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    try:
        tree = ast.parse(content, filename=filepath)
    except SyntaxError:
        return offenders

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in builtins_list:
                offender = (filepath, "function_name", node.name)
                if offender not in ALLOWLIST:
                    offenders.append(f"{filepath}:{node.lineno}: function name '{node.name}' shadows builtin")

            # Check arguments
            args = node.args.args[:]
            if hasattr(node.args, 'posonlyargs'):
                args.extend(node.args.posonlyargs)
            args.extend(node.args.kwonlyargs)

            for arg in args:
                if arg.arg in builtins_list:
                    offender = (filepath, "function_parameter", arg.arg)
                    if offender not in ALLOWLIST:
                        offenders.append(f"{filepath}:{arg.lineno}: function parameter '{arg.arg}' shadows builtin")

            if node.args.vararg and node.args.vararg.arg in builtins_list:
                offender = (filepath, "function_parameter", node.args.vararg.arg)
                if offender not in ALLOWLIST:
                    offenders.append(f"{filepath}:{node.args.vararg.lineno}: function parameter '{node.args.vararg.arg}' shadows builtin")

            if node.args.kwarg and node.args.kwarg.arg in builtins_list:
                offender = (filepath, "function_parameter", node.args.kwarg.arg)
                if offender not in ALLOWLIST:
                    offenders.append(f"{filepath}:{node.args.kwarg.lineno}: function parameter '{node.args.kwarg.arg}' shadows builtin")

        elif isinstance(node, ast.Assign):
            for target in node.targets:
                names = _get_names_from_target(target)
                for name in names:
                    if name in builtins_list:
                        offender = (filepath, "assignment", name)
                        if offender not in ALLOWLIST:
                            offenders.append(f"{filepath}:{node.lineno}: assignment to '{name}' shadows builtin")

        elif isinstance(node, ast.AnnAssign):
            names = _get_names_from_target(node.target)
            for name in names:
                if name in builtins_list:
                    offender = (filepath, "assignment", name)
                    if offender not in ALLOWLIST:
                        offenders.append(f"{filepath}:{node.lineno}: assignment to '{name}' shadows builtin")

        elif isinstance(node, ast.NamedExpr):
            names = _get_names_from_target(node.target)
            for name in names:
                if name in builtins_list:
                    offender = (filepath, "assignment", name)
                    if offender not in ALLOWLIST:
                        offenders.append(f"{filepath}:{node.lineno}: assignment to '{name}' shadows builtin")

        elif isinstance(node, ast.For):
            names = _get_names_from_target(node.target)
            for name in names:
                if name in builtins_list:
                    offender = (filepath, "assignment", name)
                    if offender not in ALLOWLIST:
                        offenders.append(f"{filepath}:{node.lineno}: assignment to '{name}' shadows builtin")

        elif isinstance(node, ast.comprehension):
            names = _get_names_from_target(node.target)
            for name in names:
                if name in builtins_list:
                    offender = (filepath, "assignment", name)
                    if offender not in ALLOWLIST:
                        offenders.append(f"{filepath}: assignment to '{name}' in comprehension shadows builtin")

        elif isinstance(node, ast.With):
            for item in node.items:
                if item.optional_vars:
                    names = _get_names_from_target(item.optional_vars)
                    for name in names:
                        if name in builtins_list:
                            offender = (filepath, "assignment", name)
                            if offender not in ALLOWLIST:
                                offenders.append(f"{filepath}:{node.lineno}: assignment to '{name}' shadows builtin")

    return offenders

def test_no_shadowing_builtins():
    files = glob.glob('*.py') + glob.glob('plugins/*.py')
    all_offenders = []

    for filepath in files:
        offenders = check_shadowing(filepath)
        all_offenders.extend(offenders)

    if all_offenders:
        error_message = "Found instances of shadowing builtins:\n" + "\n".join(all_offenders)
        pytest.fail(error_message)
