import ast
import glob
import os
import pytest

# Allowlist for existing offenders in the form 'filename.py::function_name'
ALLOWLIST = set()

def test_no_duplicate_parametrize_args():
    offenders = []

    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_files = glob.glob(os.path.join(test_dir, "test_*.py"))

    for filepath in test_files:
        filename = os.path.basename(filepath)

        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()

        try:
            tree = ast.parse(source, filename=filepath)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Call):
                        func = dec.func
                        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Attribute):
                            if (getattr(func.value.value, "id", "") == "pytest" and
                                func.value.attr == "mark" and func.attr == "parametrize"):

                                argvalues_node = None
                                if len(dec.args) >= 2:
                                    argvalues_node = dec.args[1]
                                else:
                                    for kw in dec.keywords:
                                        if kw.arg == "argvalues":
                                            argvalues_node = kw.value
                                            break

                                if argvalues_node and isinstance(argvalues_node, (ast.List, ast.Tuple)):
                                    literal_values = []
                                    is_all_literal = True

                                    for elt in argvalues_node.elts:
                                        try:
                                            # Use ast.literal_eval for robust parsing of literal items
                                            val = ast.literal_eval(elt)
                                            literal_values.append(val)
                                        except ValueError:
                                            is_all_literal = False
                                            break

                                    if is_all_literal:
                                        seen = set()
                                        has_duplicates = False
                                        for v in literal_values:
                                            try:
                                                hash_val = v
                                                hash(hash_val)
                                            except TypeError:
                                                # Unhashable type fallback (e.g. lists, dicts)
                                                hash_val = str(v)

                                            if hash_val in seen:
                                                has_duplicates = True
                                                break
                                            seen.add(hash_val)

                                        if has_duplicates:
                                            identifier = f"{filename}::{node.name}"
                                            if identifier not in ALLOWLIST:
                                                offenders.append(identifier)

    if offenders:
        pytest.fail("Found pytest.mark.parametrize decorators with duplicate literal arguments:\n" + "\n".join(offenders))
