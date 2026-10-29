import ast
import os
import pytest

MODULES_TO_CHECK = [
    'distance', 'file_loaders', 'geocode', 'humboldt',
    'llm_utils', 'tool_registry', 'validation'
]

# Allowlist of existing print statements: (filename, lineno)
ALLOWLIST = {
    ("geocode.py", 233),
    ("geocode.py", 235),
    ("geocode.py", 239),
    ("geocode.py", 240),
    ("geocode.py", 209),
    ("geocode.py", 210),
    ("geocode.py", 212),
    ("geocode.py", 213),
    ("humboldt.py", 18),
    ("humboldt.py", 256),
    ("humboldt.py", 22),
    ("humboldt.py", 38),
    ("humboldt.py", 68),
    ("humboldt.py", 70),
    ("humboldt.py", 134),
    ("humboldt.py", 138),
    ("humboldt.py", 146),
    ("humboldt.py", 184),
    ("humboldt.py", 258),
    ("humboldt.py", 166),
    ("humboldt.py", 177),
    ("humboldt.py", 191),
    ("humboldt.py", 199),
    ("humboldt.py", 219),
    ("humboldt.py", 220),
    ("humboldt.py", 221),
    ("humboldt.py", 249),
    ("humboldt.py", 251),
    ("humboldt.py", 42),
    ("humboldt.py", 46),
    ("humboldt.py", 48),
    ("humboldt.py", 50),
    ("humboldt.py", 53),
    ("humboldt.py", 65),
    ("humboldt.py", 56),

    ('distance.py', 84),
    ('geocode.py', 215),
    ('geocode.py', 217),
    ('geocode.py', 221),
    ('geocode.py', 222),
    ('humboldt.py', 17),
    ('humboldt.py', 21),
    ('humboldt.py', 36),
    ('humboldt.py', 37),
    ('humboldt.py', 41),
    ('humboldt.py', 45),
    ('humboldt.py', 47),
    ('humboldt.py', 49),
    ('humboldt.py', 52),
    ('humboldt.py', 55),
    ('humboldt.py', 57),
    ('humboldt.py', 58),
    ('humboldt.py', 59),
    ('humboldt.py', 60),
    ('humboldt.py', 61),
    ('humboldt.py', 62),
    ('humboldt.py', 63),
    ('humboldt.py', 64),
    ('humboldt.py', 67),
    ('humboldt.py', 69),
    ('humboldt.py', 141),
    ('humboldt.py', 142),
    ('humboldt.py', 143),
    ('humboldt.py', 171),
    ('humboldt.py', 173),
    ('humboldt.py', 178),
    ('humboldt.py', 180),
    ('humboldt.py', 186),
    ('humboldt.py', 192),
    ('humboldt.py', 196),
    ('humboldt.py', 200),
    ('humboldt.py', 204),
    ('humboldt.py', 209),
    ('humboldt.py', 226),
    ('humboldt.py', 237),
    ('humboldt.py', 244),
}

def test_no_print_statements_in_modules():
    offenders = []
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    for mod in MODULES_TO_CHECK:
        filename = f"{mod}.py"
        filepath = os.path.join(project_root, filename)
        if not os.path.exists(filepath):
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()

        try:
            tree = ast.parse(source, filename=filepath)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'print':
                    lineno = getattr(node, 'lineno', -1)
                    if (filename, lineno) not in ALLOWLIST:
                        offenders.append(f"{filename}:{lineno}")

    assert not offenders, f"Found unauthorized print() statements in modules: {', '.join(offenders)}"
