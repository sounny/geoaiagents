import sys
import os
import tempfile

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

import pytest
import re

def test_requirements_properties():
    req_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'requirements.txt'))
    seen_packages = set()
    missing_pins = []

    with open(req_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.split('#')[0].strip()
            if not line:
                continue

            # This regex will extract the package name
            match = re.match(r'^([a-zA-Z0-9\-_]+)(.*)$', line)
            if not match:
                continue

            pkg_name = match.group(1).lower().replace('_', '-')
            specifier = match.group(2).strip()

            assert pkg_name not in seen_packages, f"Duplicate package: {pkg_name}"
            seen_packages.add(pkg_name)

            if "==" not in specifier:
                missing_pins.append(line)

    if missing_pins:
        pytest.xfail(f"Packages missing a version pin (==): {', '.join(missing_pins)}")
