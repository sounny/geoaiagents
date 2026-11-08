import ast
import os

def test_top_level_docstrings():
    modules = ["dd2dms", "distance", "file_loaders", "geocode", "humboldt", "llm_utils", "tool_registry", "validation"]
    allowlist = {
        "dd2dms.main",
        "distance.main",
        "humboldt.build_parser",
        "humboldt.main",
        "file_loaders.test_load_geojson_point"
    }

    missing_docstrings = []

    for mod in modules:
        filepath = f"{mod}.py"
        if not os.path.exists(filepath):
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source, filename=filepath)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                name = node.name
                if not name.startswith("_"):
                    full_name = f"{mod}.{name}"
                    if full_name not in allowlist:
                        if ast.get_docstring(node) is None:
                            missing_docstrings.append(full_name)

    assert not missing_docstrings, f"Public top-level functions/classes missing docstrings: {', '.join(missing_docstrings)}"
