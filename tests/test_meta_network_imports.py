import ast
import glob
import pytest

ALLOWLIST = ['tests/test_network_block.py']

def test_meta_network_imports():
    offenders = []

    for filepath in glob.glob("tests/**/test_*.py", recursive=True):
        if filepath in ALLOWLIST:
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=filepath)

        imports_network = False
        has_mock = False

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ('socket', 'requests', 'urllib.request', 'http.client'):
                        imports_network = True
                    if 'mock' in alias.name:
                        has_mock = True
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    if node.module in ('socket', 'requests', 'urllib.request', 'http.client'):
                        imports_network = True
                    elif node.module == 'urllib' and any(a.name == 'request' for a in node.names):
                        imports_network = True
                    elif node.module == 'http' and any(a.name == 'client' for a in node.names):
                        imports_network = True

                    if 'mock' in node.module:
                        has_mock = True

                for alias in node.names:
                    if 'mock' in alias.name:
                        has_mock = True
            elif isinstance(node, ast.FunctionDef):
                for arg in node.args.args:
                    if arg.arg in ('monkeypatch', 'mock', 'mocker'):
                        has_mock = True

        if imports_network and not has_mock:
            offenders.append(filepath)

    assert not offenders, f"Tests imported network libraries without mocks: {offenders}"
