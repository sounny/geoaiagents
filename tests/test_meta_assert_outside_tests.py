import ast
import glob
import os

ALLOWLIST = []

def test_no_asserts_outside_tests():
    files_to_check = glob.glob("*.py") + glob.glob("plugins/*.py")

    offenders = []

    for filepath in files_to_check:
        if filepath.startswith("test_") or os.path.basename(filepath).startswith("test_"):
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        try:
            tree = ast.parse(content, filename=filepath)
        except SyntaxError:
            continue

        class AssertVisitor(ast.NodeVisitor):
            def __init__(self):
                self.in_test = False
                self.asserts = []

            def visit_FunctionDef(self, node):
                is_test = node.name.startswith('test_')
                old_in_test = self.in_test
                if is_test:
                    self.in_test = True

                self.generic_visit(node)
                self.in_test = old_in_test

            def visit_AsyncFunctionDef(self, node):
                self.visit_FunctionDef(node)

            def visit_ClassDef(self, node):
                is_test = node.name.startswith('Test')
                old_in_test = self.in_test
                if is_test:
                    self.in_test = True

                self.generic_visit(node)
                self.in_test = old_in_test

            def visit_Assert(self, node):
                if not self.in_test:
                    self.asserts.append(node)
                self.generic_visit(node)

        visitor = AssertVisitor()
        visitor.visit(tree)
        for node in visitor.asserts:
            offenders.append(f"{filepath}:{getattr(node, 'lineno', 0)}")

    new_offenders = [o for o in offenders if o not in ALLOWLIST]

    if new_offenders:
        msg = (
            "Found assert statements outside of tests in top-level or plugin modules. "
            "Please remove them or use appropriate error handling instead:\n"
            + "\n".join(f"  - {f}" for f in new_offenders)
        )
        assert False, msg

    # Ensure allowlist doesn't grow beyond the current count
    assert len(offenders) <= len(ALLOWLIST), "Total count of assert statements outside tests has grown beyond the allowlist."
