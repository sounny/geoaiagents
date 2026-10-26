import ast
import os
from glob import glob

def check_logging_basicconfig(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()

    tree = ast.parse(source, filename=filepath)

    class BasicConfigVisitor(ast.NodeVisitor):
        def __init__(self):
            self.calls = []
            self.in_main_guard = False

        def visit_If(self, node):
            # Check for if __name__ == "__main__":
            is_main_guard = False
            if isinstance(node.test, ast.Compare):
                if isinstance(node.test.left, ast.Name) and node.test.left.id == "__name__":
                    if len(node.test.ops) == 1 and isinstance(node.test.ops[0], ast.Eq):
                        if len(node.test.comparators) == 1 and isinstance(node.test.comparators[0], ast.Constant):
                            if node.test.comparators[0].value == "__main__":
                                is_main_guard = True

            if is_main_guard:
                old_in_main_guard = self.in_main_guard
                self.in_main_guard = True
                self.generic_visit(node)
                self.in_main_guard = old_in_main_guard
            else:
                self.generic_visit(node)

        def visit_Call(self, node):
            # Check for logging.basicConfig
            if isinstance(node.func, ast.Attribute) and node.func.attr == "basicConfig":
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "logging":
                    if not self.in_main_guard:
                        self.calls.append(node.lineno)
            self.generic_visit(node)

    visitor = BasicConfigVisitor()
    visitor.visit(tree)
    return visitor.calls

def test_no_logging_basicconfig_outside_main():
    allowlist = {

        'geoai_cli.py': [222],
        'webchat.py': [23],
        'humboldt.py': [148, 226]
    }

    files_to_check = glob('*.py') + glob('plugins/*.py')

    errors = []

    for filepath in files_to_check:
        basename = os.path.basename(filepath)
        calls = check_logging_basicconfig(filepath)

        allowed_calls = allowlist.get(basename, [])
        for call_line in calls:
            if call_line not in allowed_calls:
                errors.append(f"{filepath}:{call_line}: logging.basicConfig() called outside __main__ guard")

    assert not errors, "\n".join(errors)
