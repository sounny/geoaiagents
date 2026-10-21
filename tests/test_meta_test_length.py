import ast
from pathlib import Path

EXPECTED_OFFENDERS = {
    "test_no_sys_exit_outside_main",
    "test_control_flow_nesting_depth"
}

def test_test_function_length():
    root_dir = Path(__file__).parent
    test_files = list(root_dir.glob("test_*.py"))

    long_test_functions = set()

    for file_path in test_files:
        content = file_path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                lines = node.end_lineno - node.lineno + 1
                if lines > 80:
                    long_test_functions.add(node.name)

    new_offenders = long_test_functions - EXPECTED_OFFENDERS

    assert not new_offenders, f"New test functions longer than 80 lines found: {new_offenders}"

    assert len(long_test_functions) <= len(EXPECTED_OFFENDERS), \
        f"Total test functions longer than 80 lines ({len(long_test_functions)}) exceeds baseline ({len(EXPECTED_OFFENDERS)})"
