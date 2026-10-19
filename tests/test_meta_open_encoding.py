import ast
import glob
import pathlib

def test_open_encoding_ast():
    root_dir = pathlib.Path(__file__).parent.parent

    files = []
    files.extend(root_dir.glob("*.py"))
    files.extend((root_dir / "plugins").glob("*.py"))

    offenders = {
        "humboldt.py",
        "install_requirements.py",
    }

    errors = []

    for file_path in files:
        filepath = file_path.name
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content, filename=str(file_path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "open":
                    # Check if 'encoding' keyword argument is provided
                    has_encoding = any(kw.arg == "encoding" for kw in node.keywords)

                    # check if the mode is text
                    is_text_mode = True
                    # mode could be an arg (args[1]) or kwarg
                    if len(node.args) >= 2:
                        mode_arg = node.args[1]
                        if isinstance(mode_arg, ast.Constant) and 'b' in getattr(mode_arg, 'value', ''):
                            is_text_mode = False
                    else:
                        for kw in node.keywords:
                            if kw.arg == "mode":
                                if isinstance(kw.value, ast.Constant) and 'b' in getattr(kw.value, 'value', ''):
                                    is_text_mode = False
                                break

                    if is_text_mode and not has_encoding and filepath not in offenders:
                        errors.append(f"{filepath}:{node.lineno}: text-mode open() call missing 'encoding' argument")

    assert not errors, "\n".join(errors)
