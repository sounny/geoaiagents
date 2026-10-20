import glob
import ast
import tokenize
import io

ALLOWLIST = []

def test_no_tab_indentation():
    """
    Parses every top-level .py module and plugins/*.py with ast and fails on .py files
    whose indentation uses tab characters, with an allowlist for current offenders.
    """
    files = glob.glob("*.py") + glob.glob("plugins/*.py")
    offenders = []

    for filename in files:
        if filename in ALLOWLIST:
            continue

        with open(filename, "rb") as f:
            content = f.read()

        # Ensure it's valid Python via AST
        try:
            ast.parse(content)
        except SyntaxError:
            continue  # We only check valid python files

        # Check for tab indentation using tokenize
        try:
            tokens = tokenize.tokenize(io.BytesIO(content).readline)
            for tok in tokens:
                if tok.type == tokenize.INDENT:
                    if '\t' in tok.string:
                        offenders.append(filename)
                        break
        except tokenize.TokenError:
            pass

    assert not offenders, f"The following files use tab characters for indentation: {', '.join(offenders)}"
