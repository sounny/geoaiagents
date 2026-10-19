import ast
import glob
import os

ALLOWLIST = set()

def test_random_calls_seeded():
    """
    pytest meta-test that parses every tests/test_*.py file with ast and
    fails on random.* calls in test modules that never call random.seed()
    or use a seeded random.Random instance, with an allowlist for current offenders.
    """
    offenders = set()
    for filepath in glob.glob("tests/test_*.py"):
        filename = os.path.basename(filepath)
        if filename in ALLOWLIST or filename == "test_random_seed_meta.py":
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=filepath)
            except SyntaxError:
                continue

        has_random_call = False
        has_random_seed = False
        has_random_random = False

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    # Check for `random.X()` where value is a Name `random`
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "random":
                        if node.func.attr == "seed":
                            has_random_seed = True
                        elif node.func.attr == "Random":
                            has_random_random = True
                        else:
                            has_random_call = True

        if has_random_call and not (has_random_seed or has_random_random):
            offenders.add(filename)

    assert not offenders, f"Test modules using random.* without random.seed() or random.Random(): {sorted(list(offenders))}"
