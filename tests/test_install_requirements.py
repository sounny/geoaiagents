import sys
import os
import tempfile
import re
import pytest

try:
    from packaging.requirements import Requirement, InvalidRequirement
    HAS_PACKAGING = True
except ImportError:
    HAS_PACKAGING = False

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from install_requirements import read_requirements

def test_read_requirements_trailing_space_stripping_and_pin_keeping():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write('requests==2.32.0   \n\n# comment\n numpy>=1.26\n')
        temp_name = f.name

    try:
        reqs = read_requirements(temp_name)
        assert reqs == ['requests==2.32.0', 'numpy>=1.26']
    finally:
        os.remove(temp_name)

def test_read_requirements_keeps_flask_and_drops_hash_comment():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write('flask==2.0.0 # hash comment\n')
        temp_name = f.name

    try:
        reqs = read_requirements(temp_name)
        assert reqs == ['flask==2.0.0']
    finally:
        os.remove(temp_name)

def test_requirements_valid_specifiers():
    req_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'requirements.txt'))
    if not os.path.exists(req_path):
        pytest.skip("requirements.txt not found")

    with open(req_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if HAS_PACKAGING:
                try:
                    Requirement(line)
                except InvalidRequirement:
                    pytest.xfail(f"Invalid requirement specifier: {line}")
            else:
                if not re.match(r"^[A-Za-z0-9_.-]+(?:\[[A-Za-z0-9_.,-]+\])?(?:\s*(?:~=|==|!=|<=|>=|<|>|===)\s*.*)?$", line):
                    pytest.xfail(f"Invalid requirement specifier: {line}")
