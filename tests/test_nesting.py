import ast
import glob
import os
import pytest

ALLOWLIST = {
    'file_loaders.py': ['load_kml'],
    'humboldt.py': ['check_and_install_dependencies'],
}

def test_control_flow_nesting_depth():
    files = glob.glob("*.py") + glob.glob("plugins/*.py")

    new_offenders = set()

    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=file_path)
            except SyntaxError:
                continue # Skip files that don't parse, though they should

        class Visitor(ast.NodeVisitor):
            def __init__(self):
                self.current_function = None
                self.nesting_level = 0

            def visit_FunctionDef(self, node):
                old_function = self.current_function
                old_nesting = self.nesting_level

                self.current_function = node.name
                self.nesting_level = 0

                self.generic_visit(node)

                self.current_function = old_function
                self.nesting_level = old_nesting

            def visit_AsyncFunctionDef(self, node):
                self.visit_FunctionDef(node)

            def check_control_flow(self, node, is_elif=False):
                if self.current_function is not None:
                    # Elifs are represented as If nodes in the orelse block.
                    # We don't want to increment nesting level for an elif.
                    if not is_elif:
                        self.nesting_level += 1

                    if self.nesting_level > 5:
                        filename = os.path.basename(file_path)
                        # Check allowlist
                        if filename not in ALLOWLIST or self.current_function not in ALLOWLIST[filename]:
                            new_offenders.add(f"{file_path}:{self.current_function}")

                    # Custom generic visit for If node to detect elifs
                    if isinstance(node, ast.If):
                        for field, value in ast.iter_fields(node):
                            if field == 'body':
                                if isinstance(value, list):
                                    for item in value:
                                        self.visit(item)
                                else:
                                    self.visit(value)
                            elif field == 'orelse':
                                # Check if orelse is exactly one If node -> it's an elif
                                if isinstance(value, list) and len(value) == 1 and isinstance(value[0], ast.If):
                                    self.check_control_flow(value[0], is_elif=True)
                                elif isinstance(value, list):
                                    for item in value:
                                        self.visit(item)
                                elif value:
                                    self.visit(value)
                            else:
                                if isinstance(value, list):
                                    for item in value:
                                        if isinstance(item, ast.AST):
                                            self.visit(item)
                                elif isinstance(value, ast.AST):
                                    self.visit(value)
                    else:
                        self.generic_visit(node)

                    if not is_elif:
                        self.nesting_level -= 1
                else:
                    self.generic_visit(node)

            def visit_If(self, node):
                self.check_control_flow(node)

            def visit_For(self, node):
                self.check_control_flow(node)

            def visit_AsyncFor(self, node):
                self.check_control_flow(node)

            def visit_While(self, node):
                self.check_control_flow(node)

            def visit_With(self, node):
                self.check_control_flow(node)

            def visit_AsyncWith(self, node):
                self.check_control_flow(node)

            def visit_Try(self, node):
                # Try adds one level. Except handlers shouldn't add another level individually
                self.check_control_flow(node)

        Visitor().visit(tree)

    if new_offenders:
        offenders_str = "\n".join(sorted(new_offenders))
        pytest.fail(f"Functions exceed maximum nesting depth of 5:\n{offenders_str}")
