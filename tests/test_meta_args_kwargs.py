import ast
from pathlib import Path

# Allowlist for existing offenders.
# Format: {"filename.py:function_name"}
ALLOWLIST = set()

def get_python_files():
    root_dir = Path(__file__).parent.parent

    top_level_files = list(root_dir.glob("*.py"))
    plugin_files = list(root_dir.glob("plugins/*.py"))

    return top_level_files + plugin_files

def test_public_functions_no_args_kwargs():
    """
    Ensure that public functions in top-level Python modules and plugins
    do not accept both *args and **kwargs.
    This is enforced by an AST-based pytest meta-test using an allowlist for existing offenders.
    """
    root_dir = Path(__file__).parent.parent
    files_to_check = get_python_files()

    offenders = set()

    for filepath in files_to_check:
        # Exclude test files
        if filepath.name.startswith("test_"):
            continue

        try:
            with filepath.open("r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            continue

        try:
            tree = ast.parse(content, filename=str(filepath))
        except SyntaxError:
            continue

        rel_path = filepath.relative_to(root_dir).as_posix()

        class FunctionVisitor(ast.NodeVisitor):
            def check_function(self, node):
                if not node.name.startswith("_"):
                    if node.args.vararg is not None and node.args.kwarg is not None:
                        offenders.add(f"{rel_path}:{node.name}")

            def visit_FunctionDef(self, node):
                self.check_function(node)
                self.generic_visit(node)

            def visit_AsyncFunctionDef(self, node):
                self.check_function(node)
                self.generic_visit(node)

        FunctionVisitor().visit(tree)

    new_offenders = offenders - set(ALLOWLIST)

    assert not new_offenders, (
        "Found public functions accepting both *args and **kwargs beyond the allowlist:\n"
        + "\n".join(sorted(new_offenders))
    )
