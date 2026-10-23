import ast
from unittest.mock import patch

def test_humboldt_undocumented_public_count():
    with patch("openai.OpenAI"), patch("humboldt.check_and_install_dependencies"):
        with open("humboldt.py", "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())

        count = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if not node.name.startswith('_'):
                    if not ast.get_docstring(node):
                        count += 1

        assert count <= 3, f"Found {count} undocumented public functions/classes/methods, expected <= 3."
