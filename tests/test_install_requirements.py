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

def test_requirements_txt_is_valid():
    """Verify that all requirements in requirements.txt can be parsed by packaging.requirements."""
    import packaging.requirements

    req_file_path = os.path.join(os.path.dirname(__file__), '..', 'requirements.txt')
    reqs = read_requirements(req_file_path)

    assert len(reqs) > 0, "requirements.txt should not be empty"

    for req in reqs:
        # This will raise packaging.requirements.InvalidRequirement if the line is malformed
        packaging.requirements.Requirement(req)
