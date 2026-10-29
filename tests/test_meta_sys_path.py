import ast
import sys
from pathlib import Path

ALLOWLIST = {
    "test_webchat_infer.py",

    "test_webchat_config.py",
    "test_webchat_map.py",
    "test_install_requirements.py",
}

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
