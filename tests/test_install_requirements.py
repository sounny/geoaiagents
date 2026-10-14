import sys
import os
import tempfile
import subprocess
import pytest
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from install_requirements import read_requirements


def test_install_requirements_sh_syntax():
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'install_requirements.sh'))

    # Check syntax with bash -n
    bash_check = subprocess.run(['bash', '-n', script_path], capture_output=True, text=True)
    assert bash_check.returncode == 0, f"bash -n failed: {bash_check.stderr}"

@pytest.mark.skipif(not shutil.which("shellcheck"), reason="shellcheck not installed")
@pytest.mark.xfail(reason="Known SC2181 warning in script")
def test_install_requirements_sh_shellcheck():
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'install_requirements.sh'))

    # Check script with shellcheck
    shellcheck_check = subprocess.run(['shellcheck', script_path], capture_output=True, text=True)
    assert shellcheck_check.returncode == 0, f"shellcheck failed: {shellcheck_check.stdout}"

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
