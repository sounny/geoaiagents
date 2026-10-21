import ast
import sys
from pathlib import Path

ALLOWLIST = {
    "test_webchat_config.py",
    "test_webchat_map.py",
    "test_install_requirements.py",
    "test_webchat_infer.py",
}

def test_top_level_sys_path_modifications():
    root_dir = Path(__file__).parent.parent
    target_files = list(root_dir.glob("*.py")) + list((root_dir / "plugins").glob("*.py"))

    allowlist = {}

    total_allowed = sum(allowlist.values())
    total_found = 0
    offenders = []

    for file_path in target_files:
        if not file_path.is_file():
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=str(file_path))
            except SyntaxError:
                continue

        file_count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr in {"insert", "append"}:
                    if isinstance(node.func.value, ast.Attribute) and node.func.value.attr == "path":
                        if isinstance(node.func.value.value, ast.Name) and node.func.value.value.id == "sys":
                            file_count += 1

        if file_count > 0:
            total_found += file_count
            rel_path = file_path.relative_to(root_dir).as_posix()
            if rel_path not in allowlist or file_count > allowlist[rel_path]:
                offenders.append(f"{rel_path} ({file_count} calls)")

    assert total_found <= total_allowed, (
        f"Found {total_found} sys.path.insert/append calls in top-level and plugin modules, "
        f"exceeding the allowed total of {total_allowed}. Offenders: {', '.join(offenders)}"
    )

def test_no_sys_path_modifications():
    tests_dir = Path(__file__).parent
    offenders = []

    for test_file in tests_dir.glob("test_*.py"):
        if test_file.name in ALLOWLIST or test_file.name == "test_meta_sys_path.py":
            continue

        with open(test_file, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=str(test_file))
            except SyntaxError:
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in {"insert", "append"}:
                        if isinstance(node.func.value, ast.Attribute):
                            if node.func.value.attr == "path":
                                if isinstance(node.func.value.value, ast.Name) and node.func.value.value.id == "sys":
                                    offenders.append(f"{test_file.name}:{node.lineno}")

    assert not offenders, f"Found sys.path.insert/append in non-allowlisted test files: {', '.join(offenders)}"
