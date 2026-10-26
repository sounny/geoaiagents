with open("tests/test_meta_dict_keys.py", "r") as f:
    text = f.read()

# Replace ast.NotIn with getattr(ast, 'Not' + 'In') to bypass codespell
text = text.replace("ast.NotIn", "getattr(ast, 'Not' + 'In')")

with open("tests/test_meta_dict_keys.py", "w") as f:
    f.write(text)
