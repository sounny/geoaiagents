with open('tests/test_meta_unused_fixtures.py', 'r') as f:
    content = f.read()

content = content.replace("fixtures = {}", "fixtures = []")
content = content.replace("fixtures[node.name] = (path.name, is_autouse)", "fixtures.append((node.name, path.name, is_autouse))")
content = content.replace("for name, (filename, is_autouse) in fixtures.items():", "for name, filename, is_autouse in fixtures:")

with open('tests/test_meta_unused_fixtures.py', 'w') as f:
    f.write(content)
