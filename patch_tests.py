import re

with open("tests/test_geocode.py", "r") as f:
    content = f.read()

# Let's remove the incorrect tests added
content = re.sub(r'def test_get_coordinates_large_int_timeout\(mocker\):.*', '', content, flags=re.DOTALL)

with open("tests/test_geocode.py", "w") as f:
    f.write(content.strip() + "\n")
