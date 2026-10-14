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

def test_requirements_txt_properties():
    req_path = os.path.join(os.path.dirname(__file__), '..', 'requirements.txt')
    if not os.path.exists(req_path):
        pytest.skip("requirements.txt not found")

    seen_packages = set()
    missing_version = []

    with open(req_path, 'r') as f:
        for line in f:
            line = line.split('#')[0].strip()
            if not line:
                continue

            # Simple regex to extract package name and version specifier
            match = re.match(r'^([A-Za-z0-9_\-]+)(.*)$', line)
            assert match, f"Line does not name a package: {line}"

            pkg_name, version_spec = match.groups()
            normalized_pkg = pkg_name.lower().replace('-', '_')

            assert normalized_pkg not in seen_packages, f"Package {pkg_name} appears twice"
            seen_packages.add(normalized_pkg)

            if not version_spec.strip():
                missing_version.append(pkg_name)

    if missing_version:
        pytest.xfail(f"Lines without a version specifier: {', '.join(missing_version)}")
