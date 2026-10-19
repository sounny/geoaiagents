import ast
import glob
import os

ALLOWLIST = {
    # "filename.py": ["ClassName"]
}

def test_no_mutable_class_attributes():
    files_to_check = glob.glob("*.py") + glob.glob("plugins/*.py")

    errors = []

    for filepath in files_to_check:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        try:
            tree = ast.parse(content, filename=filepath)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                is_dataclass = False
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id == 'dataclass':
                        is_dataclass = True
                    elif isinstance(decorator, ast.Call) and getattr(decorator.func, 'id', '') == 'dataclass':
                        is_dataclass = True

                if is_dataclass:
                    continue

                class_name = node.name
                filename = os.path.basename(filepath)

                for body_node in node.body:
                    if isinstance(body_node, ast.Assign):
                        if isinstance(body_node.value, (ast.List, ast.Dict, ast.Set)):
                            if filename in ALLOWLIST and class_name in ALLOWLIST[filename]:
                                continue

                            for target in body_node.targets:
                                target_name = getattr(target, 'id', '<unknown>')
                                errors.append(f"{filepath}:{body_node.lineno} - Class '{class_name}' assigns mutable literal to attribute '{target_name}'")

                    elif isinstance(body_node, ast.AnnAssign):
                        if isinstance(body_node.value, (ast.List, ast.Dict, ast.Set)):
                            if filename in ALLOWLIST and class_name in ALLOWLIST[filename]:
                                continue

                            target_name = getattr(body_node.target, 'id', '<unknown>')
                            errors.append(f"{filepath}:{body_node.lineno} - Class '{class_name}' assigns mutable literal to attribute '{target_name}'")

    assert not errors, "Mutable class attributes found:\n" + "\n".join(errors)
