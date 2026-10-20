import ast
import glob
import pytest

ALLOWLIST = [
    # Currently empty, add offenders here if found later.
]

def test_dataclass_fields_no_mutable_default():
    files = glob.glob("*.py") + glob.glob("plugins/*.py")
    offenders = []

    for filepath in files:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        try:
            tree = ast.parse(content)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                is_dataclass = False
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Name) and dec.id == 'dataclass':
                        is_dataclass = True
                    elif isinstance(dec, ast.Attribute) and dec.attr == 'dataclass':
                        is_dataclass = True
                    elif isinstance(dec, ast.Call):
                        if isinstance(dec.func, ast.Name) and dec.func.id == 'dataclass':
                            is_dataclass = True
                        elif isinstance(dec.func, ast.Attribute) and dec.func.attr == 'dataclass':
                            is_dataclass = True

                if is_dataclass:
                    for body_item in node.body:
                        if isinstance(body_item, ast.AnnAssign) and body_item.value:
                            val = body_item.value
                            target_id = body_item.target.id if isinstance(body_item.target, ast.Name) else "unknown"
                            offender_str = f"{filepath}:{node.name}:{target_id}"

                            if offender_str in ALLOWLIST:
                                continue

                            if isinstance(val, (ast.List, ast.Dict, ast.Set)):
                                offenders.append(offender_str)
                            elif isinstance(val, ast.Call):
                                is_field = False
                                if isinstance(val.func, ast.Name) and val.func.id == 'field':
                                    is_field = True
                                elif isinstance(val.func, ast.Attribute) and val.func.attr == 'field':
                                    is_field = True

                                if is_field:
                                    for kw in val.keywords:
                                        if kw.arg == 'default' and isinstance(kw.value, (ast.List, ast.Dict, ast.Set)):
                                            offenders.append(offender_str)

    assert not offenders, f"Found mutable default in dataclass fields (should use field(default_factory=...)): {offenders}"
