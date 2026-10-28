with open("tests/test_validation.py", "r") as f:
    content = f.read()

content = "import concurrent.futures\n" + content.replace("\nimport concurrent.futures\n", "\n")

with open("tests/test_validation.py", "w") as f:
    f.write(content)
