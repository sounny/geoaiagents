import ast
from pathlib import Path
import pytest

# Mapping of "filename:ClassName" for current offenders.
ALLOWLIST = [
]

def get_python_files():
    root_dir = Path(__file__).parent.parent
    top_level_files = list(root_dir.glob("*.py"))
    plugin_files = list(root_dir.glob("plugins/*.py"))
    return top_level_files + plugin_files

def test_meta_enum_unique():
    root_dir = Path(__file__).parent.parent
    files = get_python_files()
    errors = []

    for filepath in files:
        try:
            content = filepath.read_text(encoding="utf-8")
        except Exception as e:
            continue
        try:
            tree = ast.parse(content, filename=str(filepath))
        except SyntaxError:
            continue

        rel_path = filepath.relative_to(root_dir).as_posix()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                is_enum = False
                for base in node.bases:
                    if isinstance(base, ast.Name) and "Enum" in base.id:
                        is_enum = True
                    elif isinstance(base, ast.Attribute) and "Enum" in base.attr:
                        is_enum = True

                if is_enum:
                    has_unique = any(
                        (isinstance(dec, ast.Name) and dec.id == "unique") or
                        (isinstance(dec, ast.Attribute) and dec.attr == "unique")
                        for dec in node.decorator_list
                    )

                    if not has_unique:
                        seen_values = {}
                        for stmt in node.body:
                            if isinstance(stmt, ast.Assign):
                                for target in stmt.targets:
                                    if isinstance(target, ast.Name):
                                        if isinstance(stmt.value, ast.Constant):
                                            val = stmt.value.value
                                            if val in seen_values:
                                                key = f"{rel_path}:{node.name}"
                                                if key not in ALLOWLIST:
                                                    errors.append(f"{key} assigns duplicate value {val!r} to '{target.id}' and '{seen_values[val]}', and is missing @unique intent")
                                            else:
                                                seen_values[val] = target.id

    if errors:
        pytest.fail("Enum subclasses with duplicate values lacking @unique found:\n" + "\n".join(errors))
