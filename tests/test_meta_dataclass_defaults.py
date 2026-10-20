import ast
import glob

def test_dataclass_no_mutable_defaults():
    files_to_check = glob.glob("*.py") + glob.glob("plugins/*.py")
    offenders = []
    # No existing offenders were found, but we maintain the allowlist just in case
    allowlist = []

    for filename in files_to_check:
        with open(filename, "r", encoding="utf-8") as f:
            source = f.read()

        try:
            tree = ast.parse(source, filename=filename)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                is_dataclass = False
                for dec in node.decorator_list:
                    # @dataclass
                    if isinstance(dec, ast.Name) and dec.id == "dataclass":
                        is_dataclass = True
                    # @dataclasses.dataclass
                    elif isinstance(dec, ast.Attribute) and dec.attr == "dataclass":
                        if isinstance(dec.value, ast.Name) and dec.value.id == "dataclasses":
                            is_dataclass = True
                    # @dataclass(...)
                    elif isinstance(dec, ast.Call):
                        if isinstance(dec.func, ast.Name) and dec.func.id == "dataclass":
                            is_dataclass = True
                        elif isinstance(dec.func, ast.Attribute) and dec.func.attr == "dataclass":
                            if isinstance(dec.func.value, ast.Name) and dec.func.value.id == "dataclasses":
                                is_dataclass = True

                if is_dataclass:
                    for stmt in node.body:
                        if isinstance(stmt, ast.AnnAssign) and stmt.value:
                            # Skip if type annotation is ClassVar
                            is_classvar = False
                            if isinstance(stmt.annotation, ast.Name) and stmt.annotation.id == "ClassVar":
                                is_classvar = True
                            elif isinstance(stmt.annotation, ast.Attribute) and stmt.annotation.attr == "ClassVar":
                                if isinstance(stmt.annotation.value, ast.Name) and stmt.annotation.value.id == "typing":
                                    is_classvar = True
                            elif isinstance(stmt.annotation, ast.Subscript):
                                if isinstance(stmt.annotation.value, ast.Name) and stmt.annotation.value.id == "ClassVar":
                                    is_classvar = True
                                elif isinstance(stmt.annotation.value, ast.Attribute) and stmt.annotation.value.attr == "ClassVar":
                                    if isinstance(stmt.annotation.value.value, ast.Name) and stmt.annotation.value.value.id == "typing":
                                        is_classvar = True

                            if not is_classvar:
                                if isinstance(stmt.value, (ast.List, ast.Dict, ast.Set)):
                                    offender_str = f"{filename}:{stmt.lineno}"
                                    if offender_str not in allowlist:
                                        offenders.append(offender_str)

    assert not offenders, (
        "Found dataclass fields with mutable defaults (list, dict, or set literals). "
        "Use field(default_factory=...) instead:\n" + "\n".join(offenders)
    )
